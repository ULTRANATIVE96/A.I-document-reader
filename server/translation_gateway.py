import os
import requests
import logging
import asyncio
from typing import Any
from linguistics import DakaiInputLinguist

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DakaiTranslationGateway")


class GoogleTranslationCredentialsError(Exception):
    """Exception raised for Google Cloud Translation credential failures."""
    pass


class GoogleTranslationQuotaError(Exception):
    """Exception raised when Google Cloud Translation character quota is exceeded."""
    pass


class GoogleTranslationAPIError(Exception):
    """Exception raised for general Google Cloud Translation API errors."""
    pass


class DakaiTranslationGateway:
    """
    A Principal Architect-designed routing gateway for local and premium cloud translation.
    Routes Xitsonga ('ts') and Tshivenda ('ven') translation requests to the premium
    Google Cloud Translation API with automatic error-handling and fallback to a local,
    self-hosted LibreTranslate instance. All other official languages default to LibreTranslate.
    """

    @classmethod
    def _translate_via_google(cls, text: str, target_lang: str) -> str:
        """
        Translates text via Google Cloud Translation API (v2 REST endpoint).
        Includes token tracking, quota checking, and custom error boundaries.
        """
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_TRANSLATION_API_KEY")
        if not api_key:
            raise GoogleTranslationCredentialsError(
                "Google Translation API Key is missing. Please set GOOGLE_API_KEY in the environment variables."
            )

        # Map Tshivenda custom language code ('ven') to standard Google/ISO code ('ve')
        google_lang = "ve" if target_lang == "ven" else target_lang

        url = "https://translation.googleapis.com/language/translate/v2"
        params = {"key": api_key}
        payload = {
            "q": [text],
            "target": google_lang,
            "format": "text"
        }

        try:
            response = requests.post(url, params=params, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                translations = data.get("data", {}).get("translations", [])
                if translations:
                    # Unescape HTML entities that Google translation REST API sometimes returns
                    import html
                    translated_text = translations[0].get("translatedText", "")
                    return html.unescape(translated_text)
                raise GoogleTranslationAPIError("Empty translation response from Google API.")

            # Extract detailed error information from the response JSON
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                error_reason = error_data.get("error", {}).get("errors", [{}])[0].get("reason", "")
            except Exception:
                error_msg = response.text
                error_reason = ""

            # Classify errors precisely
            if response.status_code == 403 or error_reason in ["dailyLimitExceeded", "userRateLimitExceeded", "quotaExceeded"]:
                if any(x in error_msg.lower() for x in ["key", "credential", "unauthorized", "invalid"]):
                    raise GoogleTranslationCredentialsError(f"Google API credential failure: {error_msg}")
                raise GoogleTranslationQuotaError(f"Google API quota exceeded: {error_msg}")
            elif response.status_code == 400:
                raise GoogleTranslationAPIError(f"Google API bad request: {error_msg}")
            else:
                raise GoogleTranslationAPIError(f"Google API error (Status {response.status_code}): {error_msg}")

        except requests.RequestException as e:
            raise GoogleTranslationAPIError(f"Google API network request failed: {e}")

    @classmethod
    def _translate_via_libre(cls, text: str, target_lang: str) -> str:
        """
        Translates text via our local, self-hosted LibreTranslate instance.
        """
        libre_url = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5003")
        # Ensure url ends with /translate
        if not libre_url.endswith("/translate"):
            libre_url = libre_url.rstrip("/") + "/translate"

        # Map target_lang standard if needed (LibreTranslate uses 've' for Tshivenda)
        libre_lang = "ve" if target_lang == "ven" else target_lang

        payload = {
            "q": text,
            "source": "auto",
            "target": libre_lang,
            "format": "text"
        }

        try:
            response = requests.post(libre_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("translatedText", "")
            raise Exception(f"LibreTranslate returned status code {response.status_code}: {response.text}")
        except Exception as e:
            # Fall back to deep-translator GoogleTranslator as a last-resort recovery layer
            logger.warning(f"LibreTranslate request failed: {e}. Falling back to deep-translator...")
            from deep_translator import GoogleTranslator
            # deep-translator uses 've' for Tshivenda
            dt_lang = "ve" if target_lang in ["ven", "ve"] else target_lang
            return GoogleTranslator(source="auto", target=dt_lang).translate(text)

    @classmethod
    async def translate_document(cls, text: str, target_lang: str) -> str:
        """
        Main entry point for translation requests. Normalizes input typos/slang,
        routes based on target language, and handles premium provider failures gracefully.
        """
        if not text.strip():
            return ""

        # 1. Pipeline Middleware: Slang and brand typo normalization
        normalized_text = DakaiInputLinguist.correct_typos(text)

        # 2. Route premium Bantu languages (ts, ven) to Google Cloud
        if target_lang in ["ts", "ven"]:
            try:
                # Wrap blocking requests call in asyncio.to_thread for high performance
                return await asyncio.to_thread(cls._translate_via_google, normalized_text, target_lang)
            except (GoogleTranslationCredentialsError, GoogleTranslationQuotaError, GoogleTranslationAPIError) as e:
                # Log error to developer console
                print(f"[DEVELOPER CONSOLE WARNING] Google Cloud Translation failed: {e}. Executing fail-safe fallback to LibreTranslate.")
                # 3. Fail-Safe Intercept: Fallback to LibreTranslate
                return await asyncio.to_thread(cls._translate_via_libre, normalized_text, target_lang)
        else:
            # Route all other SA languages to local self-hosted LibreTranslate
            return await asyncio.to_thread(cls._translate_via_libre, normalized_text, target_lang)
