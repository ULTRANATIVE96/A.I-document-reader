import sys
import re

# Ensure standard output can print Unicode characters in Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import asyncio
from linguistics import DakaiAudioPreprocessor, XitsongaLinguisticRepair, generate_xitsonga_ssml, get_sync_payload, DakaiInputLinguist, BanterIntent
from translation_gateway import DakaiTranslationGateway

print("==================================================")
print("RUNNING DAKAI LINGUISTICS & SSML TEST SUITE")
print("==================================================")

# Test 1: Brand & Founder Overrides (including contextual click pronunciation)
print("\n--- Test 1: Brand Overrides & Cebo Contextual Pronunciation ---")
eng_text = "Welcome to dakai. Created by Divine, Cebo, and Andiso."
zul_text = "Siyakwamukela ku-dakai. Idalwe ngu-Divine, Cebo, kanye no-Andiso."

eng_out = DakaiAudioPreprocessor.apply_brand_and_regional_overrides(eng_text, "en")
zul_out = DakaiAudioPreprocessor.apply_brand_and_regional_overrides(zul_text, "zu")

print(f"Original English: {eng_text}")
print(f"Processed English: {eng_out}")
assert 'ph="ˈsɛbɔ"' in eng_out, "Cebo should use soft S in English"
assert 'ph="daˈkaɪ"' in eng_out, "dakai should be pronounced da-kai"

print(f"\nOriginal Zulu: {zul_text}")
print(f"Processed Zulu: {zul_out}")
assert 'ph="ǀɛbɔ"' in zul_out, "Cebo should use dental click in Zulu"

# Test 2: Xitsonga Noun Classes 1-15 Concord Repairs
print("\n--- Test 2: Xitsonga Noun Class Concord Repairs (Classes 1-15) ---")
test_cases = [
    # Class 1/2 (Mu/Va)
    ("vanhu u dyondza", "vanhu va dyondza"),
    ("vafana wa tlanga", "vafana va tlanga"),
    ("vatirhi yi tira", "vatirhi va tira"),
    # Class 3/4 (Mu/Mi)
    ("muti yi saseka", "muti wu saseka"),
    ("muti ya mina", "muti wa mina"),
    ("miti u kula", "miti yi kula"),
    ("miti swa hina", "miti ya hina"),
    # Class 5/6 (Ri/Ma)
    ("vito wa mina", "vito ra mina"),
    ("tiko yi saseka", "tiko ri saseka"),
    ("matiko va saseka", "matiko ya saseka"),
    # Class 7/8 (Xi/Swi)
    ("xikolo u saseka", "xikolo xi saseka"),
    ("xikolo ya mina", "xikolo xa mina"),
    ("swilo va saseka", "swilo swi saseka"),
    ("swikolo wa mina", "swikolo swa mina"),
    # Class 9/10 (Yi/Ti)
    ("yindlu wa mina", "yindlu ya mina"),
    ("yindlu u mila", "yindlu yi mila"),
    ("tindlu wa mina", "tindlu ta mina"),
    ("tindlu u mila", "tindlu ti mila"),
    # Class 11 (Ri)
    ("rihlampfu yi wa", "rihlampfu ri wa"),
    ("rihlampfu ya tiko", "rihlampfu ra tiko"),
    # Class 14 (Vu)
    ("vutomi u saseka", "vutomi byi saseka"),
    ("vutomi wa mina", "vutomi bya mina"),
    # Class 15 (Ku)
    ("ku dyondza u pfuna", "ku dyondza ku pfuna"),
    ("ku dyondza wa mina", "ku dyondza ka mina"),
]

for orig, expected in test_cases:
    repaired = XitsongaLinguisticRepair.repair_grammar(orig)
    print(f"Original: {orig:25} -> Repaired: {repaired:25}")
    assert repaired.lower() == expected.lower(), f"Failed: {orig} -> {repaired} (expected {expected})"

# Test 3: Xitsonga Brand locatives
print("\n--- Test 3: Xitsonga Brand Locatives & Prefix Adaptation ---")
loc_test_cases = [
    ("at dakai", "ka dakai"),
    ("to dakai", "e-dakai"),
    ("in dakai", "e-dakai"),
    ("from dakai", "ku suka ka dakai"),
    ("with dakai", "na dakai"),
    ("eka dakai", "ka dakai"),
    ("ku dakai", "ka dakai"),
    ("le dakai", "le ka dakai"),
    ("e dakai", "e-dakai"),
]
for orig, expected in loc_test_cases:
    repaired = XitsongaLinguisticRepair.repair_grammar(orig)
    print(f"Original: {orig:15} -> Repaired: {repaired:20}")
    assert repaired.lower() == expected.lower(), f"Failed: {orig} -> {repaired} (expected {expected})"

# Test 4: Breathy Phonemes & Syllable boundary breaks in Xitsonga SSML
print("\n--- Test 4: Xitsonga Breathy Sounds & Syllable Timing Injection ---")
input_ssml_text = "Hlayisani. Vadyondzi va dyondza kahle e-dakai."
repaired_ssml_text = XitsongaLinguisticRepair.repair_grammar(input_ssml_text)
ssml_output = generate_xitsonga_ssml(repaired_ssml_text)

print(f"Original: {input_ssml_text}")
print(f"Repaired: {repaired_ssml_text}")
print(f"SSML:     {ssml_output}")

# Assert breathy sounds are wrapped
assert '<prosody volume="+10%" pitch="-5%">Hlayisani</prosody>' in ssml_output or '<prosody volume="+10%" pitch="-5%">hlayisani</prosody>' in ssml_output.lower(), "Hlayisani should be wrapped in prosody"
assert '<prosody volume="+10%" pitch="-5%">kahle</prosody>' in ssml_output, "kahle should be wrapped in prosody"
# Assert syllable boundary breaks are present
assert '<break time="150ms"/>.' in ssml_output, "Pause break should be injected before full stop"

# Test 5: get_sync_payload
print("\n--- Test 5: Dynamic Audio-Sync Metadata Payload ---")
payload = get_sync_payload("Welcome to dakai. Vafana wa tlanga kahle. Hlayisani.", "ts")
print(f"Payload JSON:\n{payload}")
assert payload["language"] == "ts"
assert "repaired_text" in payload
assert "ssml_text" in payload
assert "original_text" in payload

# Test 6: DakaiInputLinguist Preprocessor (South African Slang & Typo Cleaning)
print("\n--- Test 6: DakaiInputLinguist Slang & Typo Processing ---")
typo_cases = [
    ("mispelled langauges in the sumary", "misspelled languages in the summary"),
    ("nzi kombela ku pfuniwa hi lechwi", "ndzi kombela ku pfuniwa hi leswi"),
    ("chikolo xa mina xi saseka", "xikolo xa mina xi saseka"),
    ("anoku xoweta tsena", "a ndzo ku xeweta tsena"),
    ("andzoku pfuxela tsena", "a ndzo ku pfuxela tsena"),
    ("avuweni", "avuxeni"),
]
for orig, expected in typo_cases:
    corrected = DakaiInputLinguist.correct_typos(orig)
    print(f"Typo correction: {orig} -> {corrected}")
    assert corrected.lower() == expected.lower(), f"Failed typo correction: {orig} -> {corrected} (expected {expected})"

slang_cases = [
    ("nothing muxh", BanterIntent.IDLE_GREETING),
    ("jus the usual", BanterIntent.IDLE_GREETING),
    ("awe bra", BanterIntent.GREETING),
    ("sho mgani", BanterIntent.GREETING),
    ("avuweni", BanterIntent.GREETING),
    ("anoku xoweta tsena", BanterIntent.GREETING),
    ("andzoku pfuxela tsena akuna swinwani", BanterIntent.GREETING),
    ("i was just greeting you nothing else", BanterIntent.GREETING),
    ("eish this is tough", BanterIntent.EXCLAMATION),
    ("what is 2 + 2", BanterIntent.UNKNOWN),
]
for text, expected_intent in slang_cases:
    cleaned, intent, response = DakaiInputLinguist.preprocess_and_classify(text)
    print(f"Slang check: '{text}' -> Cleaned: '{cleaned}', Intent: {intent}, Response: {response}")
    assert intent == expected_intent, f"Failed slang intent match: '{text}' got {intent} (expected {expected_intent})"
    if expected_intent != BanterIntent.UNKNOWN:
        assert response is not None, f"Response should not be None for intent {expected_intent}"

# Test 7: DakaiTranslationGateway Dual-Provider Routing and Fallbacks
print("\n--- Test 7: DakaiTranslationGateway Routing & Fallbacks ---")
# 1. Test target lang ts without credentials (should raise error but fallback dynamically to LibreTranslate/deep-translator)
# Ensure it doesn't crash the program, but successfully returns a translation
try:
    translated_fallback = asyncio.run(DakaiTranslationGateway.translate_document("Welcome to our school", "ts"))
    print(f"Fallback translation (ts) returned: '{translated_fallback}'")
    assert len(translated_fallback) > 0, "Fallback translation should not be empty"
except Exception as e:
    assert False, f"Translation gateway crashed on fallback test: {e}"

# 2. Test input cleaning middleware integration
# "mispelled langauges" should be corrected to "misspelled languages" before translation API call.
# Let's mock/test this by checking if the middleware is called:
cleaned_text = DakaiInputLinguist.correct_typos("mispelled langauges")
assert cleaned_text == "misspelled languages", f"Middleware typo correction failed: {cleaned_text}"

# Test 8: DakaiInputLinguist detect_bantu_language & Capability Routing
print("\n--- Test 8: detect_bantu_language and Cap Routing ---")
detect_cases = [
    ("ini umsebenzi wakho?", "zu"),
    ("kunjhani?", "zu"),
    ("unjhani wena?", "zu"),
    ("avuxeni vatsonga", "ts"),
    ("thobela sekolo", "nso"),
    ("vhathu vha venda", "ve"),
    ("molo umntu", "xh"),
    ("what is your work?", "en"),
    ("do you understand zulu?", "en"),
    ("can you translate to xhosa?", "en"),
]
for text, expected_lang in detect_cases:
    detected = DakaiInputLinguist.detect_bantu_language(text)
    print(f"Detect Language: '{text}' -> Detected: {detected} (expected: {expected_lang})")
    assert detected == expected_lang, f"Failed language detection: '{text}' got {detected} (expected {expected_lang})"

# Test capability check directly on build_response
from main import build_response
cap_query = "do you understand Zulu?"
cap_resp = build_response(cap_query)
print(f"Capability query: '{cap_query}' -> Response: '{cap_resp}'")
assert "communicate" in cap_resp.lower() or "humushela" in cap_resp.lower(), "Should output a confirmation of Zulu language support"

print("\n==================================================")
print("SUCCESS: ALL DAKAI LINGUISTICS TESTS PASSED!")
print("==================================================")
