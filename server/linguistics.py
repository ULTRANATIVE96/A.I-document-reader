import re
import random

class DakaiAudioPreprocessor:
    """
    Scans text to inject phonetic SSML <phoneme> tags for brand identity,
    founder names, proper nouns, and localized terms, and applies phonetic tuning.
    """
    # Extensible phonetic maps for Bantu proper nouns and localized terms
    REGIONAL_OVERRIDES = {
        # Xitsonga
        "ts": {
            r"\bMalamulele\b": '<phoneme alphabet="ipa" ph="mah.lah.mu.le.le">Malamulele</phoneme>',
            r"\bGiyani\b": '<phoneme alphabet="ipa" ph="gi.ja.ni">Giyani</phoneme>',
            r"\bBushbuckridge\b": '<phoneme alphabet="ipa" ph="buʃ.bak.ridʒ">Bushbuckridge</phoneme>',
            r"\bXitsonga\b": '<phoneme alphabet="ipa" ph="ʃi.tsɔ.ŋɡa">Xitsonga</phoneme>',
            r"\bVatsonga\b": '<phoneme alphabet="ipa" ph="va.tsɔ.ŋɡa">Vatsonga</phoneme>'
        },
        # isiZulu
        "zu": {
            r"\bKwaZulu-Natal\b": '<phoneme alphabet="ipa" ph="kwa.zuː.lu.na.tal">KwaZulu-Natal</phoneme>',
            r"\beThekwini\b": '<phoneme alphabet="ipa" ph="ɛ.tʰɛ.kwi.ni">eThekwini</phoneme>',
            r"\bisiZulu\b": '<phoneme alphabet="ipa" ph="i.si.zuː.lu">isiZulu</phoneme>'
        },
        # isiXhosa
        "xh": {
            r"\bisiXhosa\b": '<phoneme alphabet="ipa" ph="i.si.kǁʰɔ.sa">isiXhosa</phoneme>',  # ǁ represents lateral click
            r"\beBhoyi\b": '<phoneme alphabet="ipa" ph="ɛ.ɓɔ.ji">eBhoyi</phoneme>'
        },
        # Tshivenda
        "ve": {
            r"\bTshivenda\b": '<phoneme alphabet="ipa" ph="tʃi.βɛ.ndda">Tshivenda</phoneme>',
            r"\bThohoyandou\b": '<phoneme alphabet="ipa" ph="tʰɔ.hɔ.ja.nddu">Thohoyandou</phoneme>'
        },
        # Sepedi
        "nso": {
            r"\bSepedi\b": '<phoneme alphabet="ipa" ph="se.pɛ.di">Sepedi</phoneme>',
            r"\bPolokwane\b": '<phoneme alphabet="ipa" ph="pɔ.lɔ.kwa.nɛ">Polokwane</phoneme>'
        }
    }

    @classmethod
    def get_brand_overrides(cls, lang_code: str = "en") -> dict:
        """
        Dynamically generates brand overrides to handle phonetic casing and language-specific click sounds.
        For example, Cebo is pronounced with a dental click /ǀɛbɔ/ in Zulu and Xhosa,
        but defaults to the soft 'S' sound /ˈsɛbɔ/ in English/other contexts.
        """
        cebo_ipa = "ǀɛbɔ" if lang_code in ["zu", "xh"] else "ˈsɛbɔ"
        return {
            r"\b(dakai|dacai)\b": r'<phoneme alphabet="ipa" ph="daˈkaɪ">\g<1></phoneme>',
            r"\bDivine\b": r'<phoneme alphabet="ipa" ph="dɪˈvaɪn">\g<0></phoneme>',
            r"\bCebo\b": f'<phoneme alphabet="ipa" ph="{cebo_ipa}">\\g<0></phoneme>',
            r"\bAndiso\b": r'<phoneme alphabet="ipa" ph="ænˈdiːɪsɔː">\g<0></phoneme>'
        }

    @classmethod
    def apply_brand_and_regional_overrides(cls, text: str, lang_code: str = "en") -> str:
        """Applies exact SSML phoneme tag overrides for Dakai brands and regional names."""
        # 1. Apply core brand overrides dynamically
        brand_overrides = cls.get_brand_overrides(lang_code)
        for pattern, replacement in brand_overrides.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # 2. Apply regional language-specific overrides
        if lang_code in cls.REGIONAL_OVERRIDES:
            for pattern, replacement in cls.REGIONAL_OVERRIDES[lang_code].items():
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                
        return text

    @classmethod
    def preserve_clicks_zulu_xhosa(cls, text: str) -> str:
        """
        Scans for Zulu and Xhosa click consonants (c, q, x) and ensures they are
        preserved. English-centric TTS engines often mispronounce words with clicks
        (e.g., pronouncing 'qaqa' as 'kaka' or 'xoxa' as 'zohza').
        This method wraps common click-containing words in their explicit IPA representations
        to protect them.
        """
        click_protections = {
            r"\bqala\b": '<phoneme alphabet="ipa" ph="ǃaːla">qala</phoneme>',  # alveolar click [!]
            r"\bxoxa\b": '<phoneme alphabet="ipa" ph="ǁɔːǁa">xoxa</phoneme>',  # lateral click [ǁ]
            r"\bcula\b": '<phoneme alphabet="ipa" ph="ǀuːla">cula</phoneme>',  # dental click [ǀ]
            r"\bqaqa\b": '<phoneme alphabet="ipa" ph="ǃaːǃa">qaqa</phoneme>',  # alveolar clicks
            r"\buxolo\b": '<phoneme alphabet="ipa" ph="uːˈǁɔːlɔ">uxolo</phoneme>', # lateral click
            r"\bcela\b": '<phoneme alphabet="ipa" ph="ǀɛːla">cela</phoneme>'   # dental click
        }
        for pattern, replacement in click_protections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    @classmethod
    def adjust_xitsonga_phonetics(cls, text: str) -> str:
        """
        Adjusts phonetics for Xitsonga by ensuring retroflex and aspirated consonants
        are properly articulated. Xitsonga uses retroflex consonants (like 't' and 'd'
        which are distinct from dental ones) and complex aspirates.
        This provides scaffolding to inject phonetic overrides for these sound systems.
        """
        xitsonga_phonetic_map = {
            r"\bdyondza\b": '<phoneme alphabet="ipa" ph="dyɔndza">dyondza</phoneme>', 
            r"\bndzi\b": '<phoneme alphabet="ipa" ph="ndzi">ndzi</phoneme>', 
            r"\bthlela\b": '<phoneme alphabet="ipa" ph="tʰlɛla">thlela</phoneme>', 
            r"\bkhari\b": '<phoneme alphabet="ipa" ph="kʰaɾi">khari</phoneme>'
        }
        for pattern, replacement in xitsonga_phonetic_map.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    @classmethod
    def balance_vowels_venda_sepedi(cls, text: str) -> str:
        """
        Balances vowel sounds in Tshivenda and Sepedi to prevent Westernized flattening.
        These languages have open/closed vowel distinctions (e.g. Sepedi e/ê, o/ô) and
        specific vowel lengths that Western TTS engines tend to shorten or mispronounce.
        """
        vowel_balancing = {
            r"\bbatho\b": '<phoneme alphabet="ipa" ph="βa.tʰɔ">batho</phoneme>', 
            r"\bmotho\b": '<phoneme alphabet="ipa" ph="mɔ.tʰɔ">motho</phoneme>', 
            r"\bvhathu\b": '<phoneme alphabet="ipa" ph="βa.tʰu">vhathu</phoneme>', 
            r"\bmuthu\b": '<phoneme alphabet="ipa" ph="mu.tʰu">muthu</phoneme>', 
        }
        for pattern, replacement in vowel_balancing.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text


class XitsongaLinguisticRepair:
    """
    Rule-based grammar post-processor to fix common machine translation errors
    in Xitsonga noun classes (Classes 1-15) and handle grammatical brand adaptation.
    """
    
    # Concord agreements & prefix corrections covering Classes 1-15
    CONCORD_REPAIRS = [
        # --- Class 1/2 (Mu- / Va-) ---
        # Fix subject and possessive concords (MT often defaults plural to u/wa/yi instead of va)
        (r'\bva([a-z]+)\s+u\b', r'va\1 va'),
        (r'\bva([a-z]+)\s+wa\b', r'va\1 va'),
        (r'\bva([a-z]+)\s+yi\b', r'va\1 va'),
        (r'\bvanhu\s+(?:u|wa|yi)\b', 'vanhu va'),
        (r'\bvasati\s+(?:u|wa|yi)\b', 'vasati va'),
        (r'\bvafana\s+(?:u|wa|yi)\b', 'vafana va'),
        (r'\bvadyondzi\s+(?:u|wa|yi)\b', 'vadyondzi va'),
        (r'\bvatirhi\s+(?:u|wa|yi)\b', 'vatirhi va'),

        # --- Class 3/4 (Mu- / Mi-) ---
        # Fix Class 3 (concord wu/wa) and Class 4 (concord yi/ya)
        (r'\bmuti\s+(?:u|yi)\b', 'muti wu'),
        (r'\bmuti\s+(?:wa|ya)\b', 'muti wa'),
        (r'\bmuri\s+(?:u|yi)\b', 'muri wu'),
        (r'\bmuri\s+(?:wa|ya)\b', 'muri wa'),
        (r'\bntiyiso\s+(?:u|yi)\b', 'ntiyiso wu'),
        (r'\bntiyiso\s+(?:wa|ya)\b', 'ntiyiso wa'),
        (r'\bnkarhi\s+(?:u|yi)\b', 'nkarhi wu'),
        (r'\bnkarhi\s+(?:wa|ya)\b', 'nkarhi wa'),
        (r'\bmi([a-z]+)\s+(?:u|va)\b', r'mi\1 yi'),
        (r'\bmi([a-z]+)\s+(?:wa|swa)\b', r'mi\1 ya'),
        (r'\bmiti\s+(?:u|va)\b', 'miti yi'),
        (r'\bmiti\s+(?:wa|swa)\b', 'miti ya'),
        (r'\bmirhi\s+(?:u|va)\b', 'mirhi yi'),
        (r'\bmirhi\s+(?:wa|swa)\b', 'mirhi ya'),

        # --- Class 5/6 (Ri- / Ma-) ---
        # Fix Class 5 (concord ri/ra) and Class 6 (concord ya)
        (r'\bribye\s+(?:u|yi)\b', 'ribye ri'),
        (r'\bribye\s+(?:wa|ya)\b', 'ribye ra'),
        (r'\bvito\s+(?:u|yi)\b', 'vito ri'),
        (r'\bvito\s+(?:wa|ya)\b', 'vito ra'),
        (r'\btiko\s+(?:u|yi)\b', 'tiko ri'),
        (r'\btiko\s+(?:wa|ya)\b', 'tiko ra'),
        (r'\bma([a-z]+)\s+(?:u|wa|va)\b', r'ma\1 ya'),
        (r'\bmavito\s+(?:u|wa|va)\b', 'mavito ya'),
        (r'\bmatiko\s+(?:u|wa|va)\b', 'matiko ya'),
        (r'\bmabye\s+(?:u|wa|va)\b', 'mabye ya'),

        # --- Class 7/8 (Xi- / Swi-) ---
        # Fix Class 7 (concord xi/xa) and Class 8 (concord swi/swa)
        (r'\bxi([a-z]+)\s+u\b', r'xi\1 xi'),
        (r'\bxi([a-z]+)\s+wa\b', r'xi\1 xa'),
        (r'\bxi([a-z]+)\s+yi\b', r'xi\1 xi'),
        (r'\bxikolo\s+(?:u|yi)\b', 'xikolo xi'),
        (r'\bxikolo\s+(?:wa|ya)\b', 'xikolo xa'),
        (r'\bxilo\s+(?:u|yi)\b', 'xilo xi'),
        (r'\bxilo\s+(?:wa|ya)\b', 'xilo xa'),
        (r'\bxitulu\s+(?:u|yi)\b', 'xitulu xi'),
        (r'\bxitulu\s+(?:wa|ya)\b', 'xitulu xa'),
        (r'\bswi([a-z]+)\s+(?:u|va)\b', r'swi\1 swi'),
        (r'\bswi([a-z]+)\s+(?:wa|ya)\b', r'swi\1 swa'),
        (r'\bswilo\s+(?:u|va)\b', 'swilo swi'),
        (r'\bswilo\s+(?:wa|ya)\b', 'swilo swa'),
        (r'\bswikolo\s+(?:u|va)\b', 'swikolo swi'),
        (r'\bswikolo\s+(?:wa|ya)\b', 'swikolo swa'),
        (r'\bswitulu\s+(?:u|va)\b', 'switulu swi'),
        (r'\bswitulu\s+(?:wa|ya)\b', 'switulu swa'),

        # --- Class 9/10 (Yi- / Ti-) ---
        # Fix Class 9 (concord yi/ya) and Class 10 (concord ti/ta)
        (r'\byindlu\s+u\b', 'yindlu yi'),
        (r'\byindlu\s+wa\b', 'yindlu ya'),
        (r'\bmbyana\s+u\b', 'mbyana yi'),
        (r'\bmbyana\s+wa\b', 'mbyana ya'),
        (r'\bti([a-z]+)\s+(?:u|va)\b', r'ti\1 ti'),
        (r'\bti([a-z]+)\s+(?:wa|ya)\b', r'ti\1 ta'),
        (r'\btindlu\s+(?:u|va)\b', 'tindlu ti'),
        (r'\btindlu\s+(?:wa|ya)\b', 'tindlu ta'),
        (r'\btimbyana\s+(?:u|va)\b', 'timbyana ti'),
        (r'\btimbyana\s+(?:wa|ya)\b', 'timbyana ta'),

        # --- Class 11 (Ri-) ---
        (r'\brihlampfu\s+(?:u|yi)\b', 'rihlampfu ri'),
        (r'\brihlampfu\s+(?:wa|ya)\b', 'rihlampfu ra'),

        # --- Class 14 (Vu-) ---
        # Fix Class 14 abstract noun concord (byi/bya)
        (r'\bvu([a-z]+)\s+(?:u|yi|va)\b', r'vu\1 byi'),
        (r'\bvu([a-z]+)\s+(?:wa|ya)\b', r'vu\1 bya'),
        (r'\bvutlhari\s+(?:u|yi|va)\b', 'vutlhari byi'),
        (r'\bvutlhari\s+(?:wa|ya)\b', 'vutlhari bya'),
        (r'\bvutomi\s+(?:u|yi|va)\b', 'vutomi byi'),
        (r'\bvutomi\s+(?:wa|ya)\b', 'vutomi bya'),
        (r'\bvusiwana\s+(?:u|yi|va)\b', 'vusiwana byi'),
        (r'\bvusiwana\s+(?:wa|ya)\b', 'vusiwana bya'),

        # --- Class 15 (Ku-) ---
        # Fix infinitive/gerund agreement (ku/ka)
        (r'\bku\s+([a-z]+)\s+(?:u|yi|va)\b', r'ku \1 ku'),
        (r'\bku\s+([a-z]+)\s+(?:wa|ya)\b', r'ku \1 ka'),
    ]

    @classmethod
    def repair_grammar(cls, text: str) -> str:
        """Applies rule-based grammatical corrections for Xitsonga translation."""
        # 1. Apply noun class concord repairs
        for pattern, replacement in cls.CONCORD_REPAIRS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # 2. Grammatical brand adaptation for "dakai" / "dacai"
        # at/in/to/from/with dakai
        text = re.sub(r'\bat\s+dakai\b', 'ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(?:in|to)\s+dakai\b', 'e-dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\bfrom\s+dakai\b', 'ku suka ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwith\s+dakai\b', 'na dakai', text, flags=re.IGNORECASE)
        
        # Same for older spelling dacai
        text = re.sub(r'\bat\s+dacai\b', 'ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(?:in|to)\s+dacai\b', 'e-dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\bfrom\s+dacai\b', 'ku suka ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwith\s+dacai\b', 'na dakai', text, flags=re.IGNORECASE)

        # Handle native translation locative combinations naturally
        # "eka dakai" -> "ka dakai" (institution/person context)
        # "e dakai" -> "e-dakai" (geographic location context)
        text = re.sub(r'\beka\s+dakai\b', 'ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\bku\s+dakai\b', 'ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\ble\s+dakai\b', 'le ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\be\s+dakai\b', 'e-dakai', text, flags=re.IGNORECASE)

        # Same for dacai
        text = re.sub(r'\beka\s+dacai\b', 'ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\bku\s+dacai\b', 'ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\ble\s+dacai\b', 'le ka dakai', text, flags=re.IGNORECASE)
        text = re.sub(r'\be\s+dacai\b', 'e-dakai', text, flags=re.IGNORECASE)

        return text


def generate_xitsonga_ssml(text: str) -> str:
    """
    Converts repaired Xitsonga text into an SSML representation with phonetic tweaks:
    1. Wraps aspirated/breathy sounds in prosody tags to mimic natural vocalization.
    2. Implements penultimate lengthening pauses at phrase boundaries.
    """
    # First apply brand and regional overrides (ensuring brand names have correct IPA tags)
    text = DakaiAudioPreprocessor.apply_brand_and_regional_overrides(text, "ts")

    # Xitsonga phonemes requiring volume boost and pitch reduction for breathy/aspirated articulation
    # h, g, dh, pf, tsw, bh, nh, dhl, th, kh, ph, hl
    breathy_pattern = re.compile(r'\b[a-zA-Z]*(?:h|g|dh|pf|tsw|bh|nh|dhl|th|kh|ph|hl)[a-zA-Z]*\b', re.IGNORECASE)

    # Split text by SSML/XML tags to avoid modifying attributes inside tags
    parts = re.split(r'(<[^>]+>)', text)
    
    for i, part in enumerate(parts):
        # If the part is an XML/SSML tag, do not modify it
        if part.startswith('<') and part.endswith('>'):
            continue
            
        # 1. Process breathy/aspirated phonemes on plain text
        words = part.split()
        processed_words = []
        for word in words:
            # Strip punctuation to inspect the core word
            clean_word = word.strip(".,!?;:()\"'")
            if breathy_pattern.search(clean_word):
                # Extract leading/trailing punctuation to keep them outside prosody tag
                leading = re.match(r"^[^a-zA-Z]*", word).group(0)
                trailing = re.search(r"[^a-zA-Z]*$", word).group(0)
                
                # Prevent negative or empty slices
                if len(trailing) > 0:
                    core = word[len(leading):len(word)-len(trailing)]
                else:
                    core = word[len(leading):]
                
                if core:
                    wrapped_word = f'{leading}<prosody volume="+10%" pitch="-5%">{core}</prosody>{trailing}'
                else:
                    wrapped_word = word
                processed_words.append(wrapped_word)
            else:
                processed_words.append(word)
        
        reconstructed_part = " ".join(processed_words)
        
        # Preserve leading/trailing space boundaries
        if part.startswith(' ') and not reconstructed_part.startswith(' '):
            reconstructed_part = ' ' + reconstructed_part
        if part.endswith(' ') and not reconstructed_part.endswith(' '):
            reconstructed_part = reconstructed_part + ' '
            
        # 2. Penultimate lengthening (phrase boundary breaks)
        # Match punctuation marks that represent phrase boundaries: [.,!?;:]
        # Insert <break time="150ms"/> before the punctuation mark.
        reconstructed_part = re.sub(r'\s*([.,!?;:])', r'<break time="150ms"/>\1', reconstructed_part)
        
        parts[i] = reconstructed_part

    # Join everything back
    ssml_content = "".join(parts)
    
    # Ensure it is wrapped in a single <speak> root, without duplicate wraps
    if ssml_content.startswith("<speak>") and ssml_content.endswith("</speak>"):
        return ssml_content
    return f"<speak>{ssml_content}</speak>"


def get_sync_payload(text: str, lang_code: str) -> dict:
    """
    Generates a synchronized JSON payload containing:
    1. original_text: Plain text representation
    2. repaired_text: Text after applying grammatical/phonetic rules
    3. ssml_text: The fully decorated SSML markup
    4. language: The language code
    """
    repaired_text = text
    if lang_code == "ts":
        repaired_text = XitsongaLinguisticRepair.repair_grammar(text)
        ssml = generate_xitsonga_ssml(repaired_text)
    else:
        # General preprocessor overrides
        repaired_text = DakaiAudioPreprocessor.apply_brand_and_regional_overrides(repaired_text, lang_code)
        
        # Apply language-specific overrides/scaffolding
        if lang_code in ["zu", "xh"]:
            repaired_text = DakaiAudioPreprocessor.preserve_clicks_zulu_xhosa(repaired_text)
        elif lang_code in ["ve", "nso"]:
            repaired_text = DakaiAudioPreprocessor.balance_vowels_venda_sepedi(repaired_text)
        
        ssml = f"<speak>{repaired_text}</speak>"

    return {
        "original_text": text,
        "repaired_text": repaired_text,
        "ssml_text": ssml,
        "language": lang_code
    }


class BanterIntent:
    IDLE_GREETING = "idle_greeting"
    GREETING = "greeting"
    SLANG_EXPRESSION = "slang_expression"
    EXCLAMATION = "exclamation"
    UNKNOWN = "unknown"


class DakaiInputLinguist:
    """
    South African localized preprocessing middleware.
    Cleans typos, maps regional slang, and classifies conversational intent to prevent
    unnecessary fallback loops or database searches.
    """
    
    # Easily extensible slang dictionary. Key: normalized term/regex, Value: intent and custom response
    SLANG_MAPPINGS = {
        # Idle small talk / "nothing much" vibe
        r"\b(nothing\s+much|nothing\s+muxh|nth\s+much|nth\s+muxh|jus\s+the\s+usual|just\s+the\s+usual|jus\s+usual|not\s+much|nothing\s+special|nothing\s+new)\b": {
            "intent": BanterIntent.IDLE_GREETING,
            "responses": [
                "Sharp sharp, let me know when you're ready to dive into some study material!",
                "Cool cool, let me know if there's any document or topic we should tackle today.",
                "Sharp sharp! Whenever you're ready, drop your document or query here."
            ]
        },
        # Greetings
        r"\b(awe|sho|sharp|heita|hola|heza|yo|sup|howdy|heya|hiya|xewani|avuxeni|sawubona|molo|ndaa|thobela|xeweta|pfuxela|greet|greeting|just\s+greeting|just\s+saying\s+hi|just\s+saying\s+hello|just\s+wanted\s+to\s+say\s+hi|just\s+wanted\s+to\s+say\s+hello|just\s+greeting\s+you|was\s+just\s+greeting)\b": {
            "intent": BanterIntent.GREETING,
            "responses": [
                "Sho! How's it going? I'm ready when you are. What study material or document are we looking at today?",
                "Awe! Ready to learn? Let me know how I can assist with your documents or studies today.",
                "Sharp sharp! I'm here to help you summarize, translate, or understand your study material. What do you have for me?"
            ]
        },
        # Local slang terms for friend/brother
        r"\b(mgani|umngani|bafethu|bra|bru|outie|chana|chommie|mzala|cuz)\b": {
            "intent": BanterIntent.SLANG_EXPRESSION,
            "responses": [
                "Awe mgani! How can I help you study today? Shoot me your document or question.",
                "Sho bra! Ready to tackle some work? Let me know what you need.",
                "Awe bafethu! Let's get to work. Drop your text or upload a file."
            ]
        },
        # Local expressions / exclamations
        r"\b(eish|jo|yoh|yo|heish|hai|aika|hayibo|hawu|heuw)\b": {
            "intent": BanterIntent.EXCLAMATION,
            "responses": [
                "Eish, I feel you! What's blocking you? Let's check it out together.",
                "Hayibo! What's the issue? Let's break it down and solve it.",
                "Eish! Sounds like a tough one. Show me the question or document and let's work it out."
            ]
        }
    }
    
    # Dictionary for common mobile typos & phonetic spelling variations in SA English and Xitsonga
    TYPO_CORRECTIONS = {
        # SA English/General typos
        r"\bmispelled\b": "misspelled",
        r"\blangauges\b": "languages",
        r"\blangauge\b": "language",
        r"\bsumary\b": "summary",
        r"\bsumarise\b": "summarise",
        r"\bsumarize\b": "summarize",
        r"\btranslator\b": "translator",
        
        # Xitsonga texting/phonetic keyboard typos (substituting 'ch'/'sh' for 'x', and 'nzi' for 'ndzi')
        r"\bchikolo\b": "xikolo",
        r"\bshikolo\b": "xikolo",
        r"\bchilo\b": "xilo",
        r"\bshilo\b": "xilo",
        r"\bchitulu\b": "xitulu",
        r"\bshitulu\b": "xitulu",
        r"\bchewani\b": "xewani",
        r"\bshewani\b": "xewani",
        r"\bchiluva\b": "xiluva",
        r"\bshiluva\b": "xiluva",
        r"\bchimanga\b": "ximanga",
        r"\bshimanga\b": "ximanga",
        r"\bchifuva\b": "xifuva",
        r"\bshifuva\b": "xifuva",
        r"\bnzi\b": "ndzi",
        r"\bnza\b": "ndza",
        r"\bnzo\b": "ndzo",
        r"\bnzilava\b": "ndzilava",
        r"\bnziku\b": "ndzi ku",
        r"\blechwi\b": "leswi",
        r"\blechwo\b": "leswo",
        r"\blexwi\b": "leswi",
        r"\blexwo\b": "leswo",
        r"\bawuxeni\b": "avuxeni",
        r"\bawuswitiv\b": "avuswitiv",
        r"\bawuswitivi\b": "avuswitiv",
        r"\bawuswitive\b": "avuswitiv",
        r"\banoku\b": "a ndzo ku",
        r"\bandzoku\b": "a ndzo ku",
        r"\bxoweta\b": "xeweta",
        r"\bavuweni\b": "avuxeni",
        r"\baxeweni\b": "xewani",
        r"\baxewani\b": "xewani",
    }

    @classmethod
    def correct_typos(cls, text: str) -> str:
        """
        Cleans and corrects common English/Bantu spelling errors and texting shortcuts.
        """
        cleaned = text
        for pattern, replacement in cls.TYPO_CORRECTIONS.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        return cleaned

    @classmethod
    def preprocess_and_classify(cls, text: str) -> tuple:
        """
        Cleans the text, checks for slang, and classifies the conversational intent.
        Returns a tuple of (cleaned_text, intent, custom_response_or_none).
        """
        # 1. Clean typos first
        cleaned_text = cls.correct_typos(text.strip())
        cleaned_lower = cleaned_text.lower()

        # 2. Match slang and small talk vibes
        for pattern, data in cls.SLANG_MAPPINGS.items():
            if re.search(pattern, cleaned_lower):
                intent = data["intent"]
                response = random.choice(data["responses"])
                return cleaned_text, intent, response
                
        # If it's a very short casual message (e.g., 1-2 words of small talk)
        # but didn't match specific slang, let's treat it as a general greeting or banter
        words = cleaned_lower.split()
        if len(words) <= 2 and any(w in ["hey", "hi", "hello", "hola", "sup", "yo", "thanks", "thank you", "ok", "okay", "sharp"] for w in words):
            return cleaned_text, BanterIntent.GREETING, "Awe! Ready to study? Let me know what you need or upload a document."

        return cleaned_text, BanterIntent.UNKNOWN, None

    @classmethod
    def detect_bantu_language(cls, text: str) -> str:
        """
        Detects if the text is in one of the supported South African Bantu languages:
        'ts' (Xitsonga), 'zu' (isiZulu), 'xh' (isiXhosa), 've' (Tshivenda), 'nso' (Sepedi).
        Uses a stop-word list and checks against English frequency to avoid false positives.
        Returns the language code if detected, otherwise 'en'.
        """
        text_lower = text.lower()
        
        # English common words and stop words to balance detection
        english_stop_words = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", 
            "do", "does", "did", "you", "your", "i", "my", "we", "our", "they", 
            "them", "he", "she", "it", "in", "on", "at", "to", "for", "with", 
            "about", "what", "who", "where", "when", "why", "how", "can", 
            "could", "would", "should", "will", "this", "that", "these", "those",
            "welcome", "study", "partner", "document", "ask", "anything", "math",
            "hello", "there", "name", "divine", "cebo", "andiso", "dakai", "dacai",
            "understand", "language", "speak", "translate", "write", "about", "say"
        }
        
        bantu_words = {
            "ts": [
                "avuxeni", "xewani", "khensa", "ngopfu", "swinene", "ndza", "ndzi", "ku", "dyondza", "hlaya", 
                "vanhu", "vasati", "vafana", "xikolo", "xilo", "xitulu", "swilo", "misava", "tiko", 
                "vito", "ribye", "yindlu", "tindlu", "timbyana", "mbyana", "hlayisani", "kahle", 
                "tlanga", "saseka", "tsonga", "vatsonga", "xitsonga", "leswi", "leswo", "malamulele", "giyani",
                "leswaku", "yini", "tivi", "switivi", "switive", "switiva", "niri"
            ],
            "zu": [
                "sawubona", "sanibonani", "yebo", "cha", "kunjhani", "unjhani", "ngiyaphila", "ngiyabonga", 
                "kakhulu", "isizulu", "zulu", "umuntu", "abantu", "isikole", "indlu", "ngiya", "uya", 
                "baya", "futhi", "khona", "kanye", "ngani", "namhlanje", "kusasa", "izolo", "umsebenzi", 
                "wakho", "ini", "yini", "ubani", "igama", "cela", "sicela", "uxolo", "xoxa", "qala", "cula"
            ],
            "xh": [
                "molo", "molweni", "enkosi", "kakhulu", "isixhosa", "xhosa", "umntu", "abantu", "isikole", 
                "indlu", "ndiya", "uya", "baya", "namhlanje", "ngomso", "izolo", "umsebenzi", "wakho", 
                "intoni", "yintoni", "ubani", "igama", "cela", "sicela", "uxolo", "xoxa", "qala", "cula"
            ],
            "ve": [
                "ndaa", "aa", "venda", "tshivenda", "vhathu", "muthu", "tshikolo", "ndi", "khou", "ri", 
                "livhuwa", "maanda", "tenda", "musi", "nga", "zwino", "shango", "dzina"
            ],
            "nso": [
                "thobela", "sepedi", "pedi", "batho", "motho", "sekolo", "ke", "a", "leboga", "kudu", 
                "lehono", "kamoso", "maabane", "mosomo", "gago", "eng", "leina", "kgopela"
            ]
        }
        
        scores = {lang: 0 for lang in bantu_words}
        eng_score = 0
        
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if word in english_stop_words:
                eng_score += 1
            for lang, word_list in bantu_words.items():
                if word in word_list:
                    scores[lang] += 1
                    
        best_bantu_lang = "en"
        best_bantu_score = 0
        for lang, score in scores.items():
            if score > best_bantu_score:
                best_bantu_score = score
                best_bantu_lang = lang
                
        if eng_score >= best_bantu_score:
            return "en"
            
        if best_bantu_lang == "en" or best_bantu_score == 0:
            if re.search(r'\b(?:ndzi|ndza|leswi|xikolo|swilo|leswaku|avuxeni|awuxeni|switivi|switive|xitsonga)\b', text_lower):
                return "ts"
            if re.search(r'\b(?:ngiya|sawubona|kunjhani|umsebenzi|wakho|isizulu)\b', text_lower):
                return "zu"
            if re.search(r'\b(?:ndiya|enkosi|molo|isixhosa)\b', text_lower):
                return "xh"
            if re.search(r'\b(?:ndi khou|vhathu|tshikolo|livhuwa)\b', text_lower):
                return "ve"
            if re.search(r'\b(?:ke a|thobela|batho|sekolo)\b', text_lower):
                return "nso"
                
        return best_bantu_lang

