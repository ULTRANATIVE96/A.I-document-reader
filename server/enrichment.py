"""
Bantu Language Post-Translation Enrichment Engine
Corrects common machine-translation errors for SA languages.
"""
import re

# ----------------------------------------------------------------
# Xitsonga (ts) — Noun class prefixes, locatives, tense markers
# ----------------------------------------------------------------
XITSONGA_CORRECTIONS = {
    # Noun class fixes
    r'\bthe\s+': '',                         # No articles in Xitsonga
    r'\ba\s+': '',
    r'\ban\s+': '',
    r'\bni\s+ku\b': 'ndzi ku',              # 1st person "I"
    r'\bhi\s+ku\b': 'hi ku',                # 1st person plural
    r'\bva\s+le\b': 'va le',                # "they are at"
    r'\bendzhaku\b': 'endzhaku',            # "after/behind"
    r'\bndzawu\b': 'ndhawu',               # "place"
    r'\bsikolo\b': 'xikolo',               # "school" (xi- class)
    r'\bsilo\b': 'xilo',                    # "thing"
    r'\bsitulu\b': 'xitulu',               # "chair"
    r'\bswilo\b': 'swilo',                  # plural things
    r'\bmuhlaba\b': 'misava',               # "world/earth"
}

XITSONGA_DIALECTS = {
    "malamulele": {
        r'\bndzi\b': 'ndzi',
        r'\bku\s+dyondza\b': 'ku dyondza',
    },
    "bushbuckridge": {
        r'\bndzi\b': 'ndzi',
        r'\bku\s+dyondza\b': 'ku hlaya',    # regional variant for "learn/read"
    },
    "giyani": {
        r'\bku\s+dyondza\b': 'ku dyondza',
    },
}

# ----------------------------------------------------------------
# isiZulu (zu) — Noun class agreement, possessive concords
# ----------------------------------------------------------------
ISIZULU_CORRECTIONS = {
    r'\bthe\s+': '',
    r'\ba\s+': '',
    r'\ban\s+': '',
    r'\bumuntu\s+ba\b': 'umuntu u',          # Class 1 concord
    r'\babantu\s+u\b': 'abantu ba',          # Class 2 concord
    r'\bisikole\b': 'isikole',               # school
    r'\bindlu\b': 'indlu',                    # house
    r'\bngi\s+ya\b': 'ngiya',                # "I am" contraction
    r'\bu\s+ya\b': 'uya',                    # "you are"
    r'\bba\s+ya\b': 'baya',                  # "they are"
}

ISIZULU_DIALECTS = {
    "kwazulu-natal": {},
    "gauteng-urban": {
        r'\byebo\b': 'ja',                    # Urban slang for "yes"
        r'\bsawubona\b': 'awu',               # Shortened greeting
    },
}

# ----------------------------------------------------------------
# isiXhosa (xh) — Click consonant context, aspirated stops
# ----------------------------------------------------------------
ISIXHOSA_CORRECTIONS = {
    r'\bthe\s+': '',
    r'\ba\s+': '',
    r'\bumtu\b': 'umntu',                     # person
    r'\babantu\b': 'abantu',                  # people
    r'\bisikolo\b': 'isikolo',                # school
    r'\bndi\s+ya\b': 'ndiya',                 # "I am" contraction
    r'\bu\s+ya\b': 'uya',
}

ISIXHOSA_DIALECTS = {
    "eastern-cape": {},
    "western-cape": {
        r'\bmolo\b': 'molo',
    },
}

# ----------------------------------------------------------------
# Tshivenda (ve) — Tone-marking, class 1/2 prefixes
# ----------------------------------------------------------------
TSHIVENDA_CORRECTIONS = {
    r'\bthe\s+': '',
    r'\ba\s+': '',
    r'\bmuthu\b': 'muthu',                    # person
    r'\bvhathu\b': 'vhathu',                  # people
    r'\btshikolo\b': 'tshikolo',              # school
    r'\bndi\s+khou\b': 'ndi khou',            # "I am" progressive
    r'\bri\s+khou\b': 'ri khou',              # "we are"
}

TSHIVENDA_DIALECTS = {
    "venda": {},
    "limpopo": {},
}

# ----------------------------------------------------------------
# Sepedi (nso) — Labial assimilation, borrowed word adaptation
# ----------------------------------------------------------------
SEPEDI_CORRECTIONS = {
    r'\bthe\s+': '',
    r'\ba\s+': '',
    r'\bmotho\b': 'motho',                    # person
    r'\bbatho\b': 'batho',                    # people
    r'\bsekolo\b': 'sekolo',                  # school
    r'\bke\s+a\b': 'ke a',                    # "I am"
    r'\bo\s+a\b': 'o a',                      # "you are"
    r'\bba\s+a\b': 'ba a',                    # "they are"
}

SEPEDI_DIALECTS = {
    "polokwane": {},
    "sekhukhune": {},
}

# ----------------------------------------------------------------
# Master registry
# ----------------------------------------------------------------
LANG_CORRECTIONS = {
    "ts": XITSONGA_CORRECTIONS,
    "zu": ISIZULU_CORRECTIONS,
    "xh": ISIXHOSA_CORRECTIONS,
    "ve": TSHIVENDA_CORRECTIONS,
    "nso": SEPEDI_CORRECTIONS,
}

LANG_DIALECTS = {
    "ts": XITSONGA_DIALECTS,
    "zu": ISIZULU_DIALECTS,
    "xh": ISIXHOSA_DIALECTS,
    "ve": TSHIVENDA_DIALECTS,
    "nso": SEPEDI_DIALECTS,
}

# Formality swaps: { lang: { word: (formal, colloquial) } }
FORMALITY_PAIRS = {
    "ts": {
        "ndza khensa": ("ndza khensa ngopfu", "ndza khensa"),     # thank you
        "avuxeni": ("Avuxeni", "Awe"),                            # good morning
        "xewani": ("Xewani", "Heyi"),                             # hello
    },
    "zu": {
        "sawubona": ("Sawubona", "Awu"),
        "ngiyabonga": ("Ngiyabonga kakhulu", "Ngiyabonga"),
        "yebo": ("Yebo", "Ja"),
    },
    "xh": {
        "molo": ("Molo", "Ewe"),
        "enkosi": ("Enkosi kakhulu", "Enkosi"),
    },
    "ve": {
        "ndaa": ("Ndaa", "Awe"),
        "ndi a livhuwa": ("Ndi a livhuwa nga maanda", "Ndi a livhuwa"),
    },
    "nso": {
        "thobela": ("Thobela", "Awe"),
        "ke a leboga": ("Ke a leboga kudu", "Ke a leboga"),
    },
}


def post_translate_enrich(text, lang_code):
    """
    Apply regex-based corrections to machine-translated text.
    Returns corrected text.
    """
    corrections = LANG_CORRECTIONS.get(lang_code, {})
    result = text
    for pattern, replacement in corrections.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def apply_dialect(text, lang_code, dialect):
    """
    Apply regional dialect adjustments.
    """
    dialects = LANG_DIALECTS.get(lang_code, {})
    dialect_rules = dialects.get(dialect, {})
    result = text
    for pattern, replacement in dialect_rules.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def adjust_formality(text, lang_code, level=0.5):
    """
    Adjust formality: 0.0 = fully colloquial, 1.0 = fully formal.
    """
    pairs = FORMALITY_PAIRS.get(lang_code, {})
    result = text
    for word, (formal, colloquial) in pairs.items():
        if level >= 0.5:
            result = result.replace(colloquial, formal)
        else:
            result = result.replace(formal, colloquial)
    return result


def get_available_dialects(lang_code):
    """Return list of available dialects for a language."""
    dialects = LANG_DIALECTS.get(lang_code, {})
    return list(dialects.keys())


def enrich_translation(text, lang_code, dialect=None, formality=0.5):
    """
    Full enrichment pipeline:
    1. Post-translation corrections
    2. Dialect adjustments
    3. Formality tuning
    """
    result = post_translate_enrich(text, lang_code)
    if dialect:
        result = apply_dialect(result, lang_code, dialect)
    result = adjust_formality(result, lang_code, formality)
    return result
