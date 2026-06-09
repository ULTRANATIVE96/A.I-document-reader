import re
import os
import asyncio
import json
import math
import random
import operator
import long_responses as long
from flask import Flask, request, jsonify
from flask_cors import CORS
import wikipedia
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

wikipedia.set_lang("en")

# ----------------------------------------------------------------
# Paths
# ----------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "learned_memory.json")

# ----------------------------------------------------------------
# Persistent Learned Memory
# ----------------------------------------------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"learned_facts": []}

def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Memory save error: {e}")

memory_store = load_memory()

# ----------------------------------------------------------------
# Conversation Sessions
# ----------------------------------------------------------------
sessions = {}
MAX_HISTORY = 20

def get_history(session_id):
    return sessions.get(session_id, [])

def push_history(session_id, role, content):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"role": role, "content": content})
    if len(sessions[session_id]) > MAX_HISTORY:
        sessions[session_id] = sessions[session_id][-MAX_HISTORY:]

def last_user_topic(session_id):
    """Get the last topic the user discussed."""
    history = get_history(session_id)
    for turn in reversed(history):
        if turn["role"] == "user":
            return turn["content"]
    return ""

# ----------------------------------------------------------------
# Math Evaluator — supports symbols AND words
# ----------------------------------------------------------------
WORD_TO_OP = {
    "plus": "+", "add": "+", "added": "+", "and": "+",
    "minus": "-", "subtract": "-", "subtracted": "-", "less": "-",
    "times": "*", "multiplied": "*", "multiply": "*", "by": "*",
    "divided": "/", "divide": "/", "over": "/",
    "squared": "**2", "cubed": "**3",
    "percent": "/100",
}
WORD_TO_NUM = {
    "zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5",
    "six":"6","seven":"7","eight":"8","nine":"9","ten":"10",
    "eleven":"11","twelve":"12","thirteen":"13","fourteen":"14","fifteen":"15",
    "sixteen":"16","seventeen":"17","eighteen":"18","nineteen":"19","twenty":"20",
    "thirty":"30","forty":"40","fifty":"50","sixty":"60","seventy":"70",
    "eighty":"80","ninety":"90","hundred":"*100","thousand":"*1000",
}

def words_to_expr(text):
    """Convert word-based math to a symbol expression."""
    words = text.lower().split()
    out = []
    for w in words:
        if w in WORD_TO_NUM:
            out.append(WORD_TO_NUM[w])
        elif w in WORD_TO_OP:
            out.append(WORD_TO_OP[w])
        elif re.match(r'^[\d\.\+\-\*\/\(\)\^]+$', w):
            out.append(w)
    return " ".join(out)

def safe_eval_math(expr):
    import ast as _ast
    expr = expr.strip().replace("^", "**")
    try:
        tree = _ast.parse(expr, mode="eval")
    except SyntaxError:
        return None, False

    SAFE_OPS = {
        "Add": operator.add, "Sub": operator.sub, "Mult": operator.mul,
        "Div": operator.truediv, "Pow": operator.pow, "Mod": operator.mod,
        "FloorDiv": operator.floordiv, "USub": operator.neg,
    }
    SAFE_FUNCS = {
        "sqrt": math.sqrt, "abs": abs, "round": round, "pow": pow,
        "floor": math.floor, "ceil": math.ceil, "log": math.log,
        "log10": math.log10, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    }

    class Visitor(_ast.NodeVisitor):
        def visit_Expression(self, node): return self.visit(node.body)
        def visit_Constant(self, node):
            if isinstance(node.value, (int, float)): return node.value
            raise ValueError
        def visit_BinOp(self, node):
            fn = SAFE_OPS.get(type(node.op).__name__)
            if not fn: raise ValueError
            return fn(self.visit(node.left), self.visit(node.right))
        def visit_UnaryOp(self, node):
            fn = SAFE_OPS.get(type(node.op).__name__)
            if not fn: raise ValueError
            return fn(self.visit(node.operand))
        def visit_Call(self, node):
            if isinstance(node.func, _ast.Name) and node.func.id in SAFE_FUNCS:
                return SAFE_FUNCS[node.func.id](*[self.visit(a) for a in node.args])
            raise ValueError
        def generic_visit(self, node): raise ValueError

    try:
        result = Visitor().visit(tree)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return result, True
    except Exception:
        return None, False

def extract_math(text):
    """Try both symbol-based and word-based math extraction."""
    t = text.lower().strip()

    # Symbol patterns first
    sym_patterns = [
        r'(?:what\s+is|calculate|compute|solve|eval(?:uate)?)\s+([\d\s\+\-\*\/\^\(\)\.%]+(?:sqrt|abs|round|floor|ceil|log\d*|sin|cos|tan)?[\d\s\+\-\*\/\^\(\)\.]*)',
        r'^([\d\s\+\-\*\/\%\^\(\)\.]+)\s*[=?]?\s*$',
        r'((?:sqrt|abs|floor|ceil|log\d*|sin|cos|tan)\s*\([\d\s\+\-\*\/\.\,]+\))',
    ]
    for pat in sym_patterns:
        m = re.search(pat, t, re.IGNORECASE)
        if m:
            expr = m.group(1).strip()
            result, ok = safe_eval_math(expr)
            if ok:
                return result, expr

    # Word-based math — detect if message is a math question
    math_triggers = ["what is", "calculate", "compute", "solve", "how much is", "whats", "what's"]
    has_trigger = any(trigger in t for trigger in math_triggers)
    has_num_word = any(w in t for w in WORD_TO_NUM)
    has_op_word = any(w in t for w in WORD_TO_OP)

    if (has_trigger or has_num_word) and has_op_word:
        expr = words_to_expr(t)
        result, ok = safe_eval_math(expr)
        if ok:
            return result, expr

    return None, None

# ----------------------------------------------------------------
# Pronunciation Guide
# ----------------------------------------------------------------
# Common pronunciation rules for English
PHONEME_MAP = [
    # Multi-char rules first
    (r'tion', 'shun'), (r'sion', 'zhun'), (r'ph', 'f'), (r'gh', ''),
    (r'kn', 'n'), (r'wr', 'r'), (r'ck', 'k'), (r'qu', 'kw'),
    (r'ch', 'ch'), (r'sh', 'sh'), (r'th', 'th'), (r'wh', 'w'),
    (r'ng', 'ng'), (r'dge', 'j'), (r'ge', 'j'), (r'ce', 's'),
    (r'ci', 's'), (r'cy', 's'), (r'gi', 'j'), (r'gy', 'j'),
    (r'ai', 'ay'), (r'ay', 'ay'), (r'ea', 'ee'), (r'ee', 'ee'),
    (r'ie', 'ee'), (r'oa', 'oh'), (r'oe', 'oh'), (r'oo', 'oo'),
    (r'ou', 'ow'), (r'ow', 'oh'), (r'ue', 'yoo'), (r'ui', 'oo'),
    (r'au', 'aw'), (r'aw', 'aw'), (r'oi', 'oy'), (r'oy', 'oy'),
    # Trailing silent e
    (r'a(.)e$', r'ay\1'), (r'i(.)e$', r'eye\1'), (r'o(.)e$', r'oh\1'), (r'u(.)e$', r'yoo\1'),
]

SYLLABLE_STRESS = {
    1: "", 2: "·", 3: "-", 4: "·",
}

def get_syllable_count(word):
    word = word.lower()
    count = len(re.findall(r'[aeiouy]+', word))
    if word.endswith('e') and len(word) > 2 and word[-2] not in 'aeiouy':
        count = max(1, count - 1)
    return max(1, count)

def pronounce_word(word):
    """Generate a simple phonetic pronunciation for any English word."""
    word = word.strip().lower()
    if not word or not re.match(r'^[a-z]+$', word):
        return None

    # Known pronunciations — curated for accuracy
    known = {
        # dakai ecosystem
        "dakai": "da-KAI", "dacai": "da-KAI", "divine": "dih-VINE", "andiso": "an-DEE-so", "cebo": "SEH-bo",
        # Common English names
        "kevin": "KEV-in", "david": "DAY-vid", "michael": "MY-kul", "james": "jaymz",
        "john": "jon", "robert": "ROB-ert", "william": "WIL-yum", "richard": "RICH-ard",
        "joseph": "JO-sef", "thomas": "TOM-us", "charles": "charlz", "christopher": "KRIS-tuh-fer",
        "daniel": "DAN-yul", "matthew": "MATH-yoo", "anthony": "AN-thuh-nee",
        "jessica": "JES-ih-kah", "sarah": "SAR-uh", "jennifer": "JEN-ih-fer",
        "elizabeth": "eh-LIZ-uh-beth", "mary": "MAR-ee", "patricia": "pah-TRISH-uh",
        "linda": "LIN-dah", "barbara": "BAR-brah", "margaret": "MAR-gret",
        "michelle": "mih-SHEL", "stephanie": "STEF-uh-nee", "nicole": "nih-KOHL",
        # South African names
        "thabo": "TAH-bo", "sipho": "SEE-po", "nomsa": "NOM-sah", "bongani": "bon-GAH-nee",
        "zanele": "zah-NEH-leh", "mandla": "MAHN-dlah", "lerato": "leh-RAH-toh",
        "naledi": "nah-LEH-dee", "tshepo": "TSHEH-po", "kagiso": "kah-GEE-so",
        "mandela": "man-DEH-lah", "zuma": "ZOO-mah", "ramaphosa": "rah-mah-POH-sah",
        "matimba": "mah-TIM-bah", "tsonga": "TSONG-ah",
        # Tricky English words
        "the": "thuh", "a": "ay", "queue": "kyoo", "colonel": "KER-nel",
        "yacht": "yot", "knife": "nyfe", "knight": "nyte", "gnome": "nome",
        "chaos": "KAY-os", "choir": "KWHY-er", "lieutenant": "lef-TEN-ant",
        "worcester": "WOO-ster", "gloucester": "GLOS-ter", "hawaii": "hah-WY-ee",
        "february": "FEB-roo-air-ee", "wednesday": "WENZ-day",
        "america": "ah-MER-ih-kah", "united": "yoo-NY-ted", "states": "staytes",
        "president": "PREZ-ih-dent", "pronunciation": "proh-NUN-see-AY-shun",
        "recipe": "RES-ih-pee", "mischievous": "MIS-chuh-vus", "hyperbole": "hy-PER-boh-lee",
        "epitome": "eh-PIT-oh-mee", "segue": "SEG-way", "niche": "neesh",
        "genre": "ZHON-ruh", "entrepreneur": "on-truh-pruh-NUR",
        "quinoa": "KEEN-wah", "acai": "ah-sah-EE", "espresso": "eh-SPREH-so",
    }
    if word in known:
        return known[word]

    # Syllable split attempt
    syllables = re.findall(r'[^aeiouy]*[aeiouy]+(?:[^aeiouy]*(?=$|[^aeiouy]))?', word)
    if not syllables:
        syllables = [word]

    phonetic = "-".join(s.upper() if i == len(syllables) - 1 else s for i, s in enumerate(syllables))
    return phonetic if phonetic else word.upper()

def handle_pronunciation(user_input):
    """Detect pronunciation questions and answer them."""
    patterns = [
        r'how\s+(?:do\s+(?:you|i)|to)\s+(?:say|pronounce|read)\s+(.+)',
        r'(?:pronounce|pronunciation\s+of|how\s+is\s+.+\s+said|say)\s+(.+)',
        r'what(?:\'s|\s+is)\s+the\s+pronunciation\s+of\s+(.+)',
    ]
    for pat in patterns:
        m = re.search(pat, user_input.lower().strip(), re.IGNORECASE)
        if m:
            raw_word = m.group(1).strip().strip('?.,!').strip()
            words = raw_word.split()
            results = []
            for w in words[:10]:
                p = pronounce_word(w)
                if p:
                    results.append(f"• {w.capitalize()}: {p}")
            if results:
                header = "Here's the pronunciation breakdown:\n\n"
                return header + "\n".join(results)
    return None

# ----------------------------------------------------------------
# Wikipedia — real general knowledge
# ----------------------------------------------------------------
def search_wikipedia(query):
    """Search Wikipedia and return a concise summary."""
    try:
        # Clean the query
        q = re.sub(r'^(who|what|where|when|why|how|is|are|was|were)\s+(is|are|was|were|the|a|an)?\s*', '', query, flags=re.IGNORECASE).strip()
        if not q:
            q = query

        results = wikipedia.search(q, results=5)
        if not results:
            return None

        for title in results:
            try:
                summary = wikipedia.summary(title, sentences=3, auto_suggest=False)
                if summary and len(summary) > 50:
                    # Trim to 3 sentences max
                    sentences = re.split(r'(?<=[.!?])\s+', summary)
                    return " ".join(sentences[:3])
            except wikipedia.DisambiguationError as e:
                # Try first disambiguation option
                try:
                    summary = wikipedia.summary(e.options[0], sentences=3)
                    sentences = re.split(r'(?<=[.!?])\s+', summary)
                    return " ".join(sentences[:3])
                except Exception:
                    continue
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"Wikipedia error: {e}")
        return None

def is_knowledge_question(text):
    """Detect if this is a general knowledge / factual question."""
    knowledge_triggers = [
        r'^who\s+is', r'^who\s+was', r'^what\s+is', r'^what\s+was', r'^what\s+are',
        r'^where\s+is', r'^when\s+did', r'^when\s+was', r'^how\s+many',
        r'^tell\s+me\s+about', r'^what\s+do\s+you\s+know\s+about',
        r'^explain\s+', r'^describe\s+', r'^define\s+', r'^what\s+does\s+.+\s+mean',
        r'^who\s+are', r'^give\s+me\s+info', r'^history\s+of',
    ]
    t = text.lower().strip()
    for pat in knowledge_triggers:
        if re.search(pat, t):
            return True
    return False

# ----------------------------------------------------------------
# Hardcoded Facts DB — direct factual answers (Rule 1)
# ----------------------------------------------------------------
FACTS_DB = {
    # World leaders
    "president of the united states": "The current president of the United States is Donald Trump (47th president, sworn into office in January 2025).",
    "president of america": "The current president of the United States is Donald Trump (47th president, sworn into office in January 2025).",
    "usa president": "The current president of the United States is Donald Trump (47th president, sworn into office in January 2025).",
    "president of south africa": "The current president of South Africa is Cyril Ramaphosa, serving since February 2018.",
    "president of russia": "The current president of Russia is Vladimir Putin.",
    "president of china": "The current president of China is Xi Jinping.",
    "prime minister of uk": "The current Prime Minister of the United Kingdom is Keir Starmer, since July 2024.",
    "prime minister of england": "The current Prime Minister of the United Kingdom is Keir Starmer, since July 2024.",
    # Geography
    "capital of south africa": "South Africa has three capital cities: Pretoria (executive), Cape Town (legislative), and Bloemfontein (judicial).",
    "capital of usa": "The capital of the United States is Washington, D.C.",
    "capital of america": "The capital of the United States is Washington, D.C.",
    "capital of france": "The capital of France is Paris.",
    "capital of japan": "The capital of Japan is Tokyo.",
    "capital of china": "The capital of China is Beijing.",
    "capital of germany": "The capital of Germany is Berlin.",
    "capital of nigeria": "The capital of Nigeria is Abuja.",
    "capital of kenya": "The capital of Kenya is Nairobi.",
    # Science
    "speed of light": "The speed of light in a vacuum is approximately 299,792,458 metres per second (about 300,000 km/s).",
    "boiling point of water": "Water boils at 100°C (212°F) at standard atmospheric pressure.",
    "freezing point of water": "Water freezes at 0°C (32°F) at standard atmospheric pressure.",
    # General
    "largest country": "Russia is the largest country in the world by area, spanning over 17 million km².",
    "smallest country": "Vatican City is the smallest country in the world, at only 0.44 km².",
    "largest ocean": "The Pacific Ocean is the largest ocean, covering about 165.25 million km².",
    "tallest mountain": "Mount Everest is the tallest mountain above sea level, standing at 8,849 metres (29,032 ft).",
}

def lookup_fact(text):
    """Check if the user's question matches a known fact."""
    t = text.lower().strip().rstrip('?.,!')
    # Remove common question prefixes
    for prefix in ["who is the", "who is", "what is the", "what is", "what's the", "what's",
                    "where is the", "where is", "tell me the", "tell me about the", "tell me about"]:
        if t.startswith(prefix):
            key = t[len(prefix):].strip()
            if key in FACTS_DB:
                return FACTS_DB[key]
    # Direct key match
    for key, val in FACTS_DB.items():
        if key in t:
            return val
    return None

# ----------------------------------------------------------------
# Tonal Intelligence — context-aware response builder
# ----------------------------------------------------------------
def translate_back_if_needed(text: str, lang_code: str) -> str:
    """Helper to translate the final response string back to the user's language."""
    if lang_code == "en":
        return text
    try:
        return GoogleTranslator(source="en", target=lang_code).translate(text)
    except Exception as e:
        print(f"Translation back to {lang_code} failed: {e}")
        return text

def build_response(user_input, context="", session_id=None, target_lang=None):
    # Preprocess user input: correct typos, map slang, and classify conversational intent
    cleaned_text, intent, slang_response = DakaiInputLinguist.preprocess_and_classify(user_input)

    # Detect if the query is in a Bantu language
    detected_lang = DakaiInputLinguist.detect_bantu_language(cleaned_text)
    
    # Active language is either the detected Bantu language, or the user's target selection
    active_lang = detected_lang if detected_lang != "en" else (target_lang or "en")

    if intent != BanterIntent.UNKNOWN:
        return translate_back_if_needed(slang_response, active_lang)

    is_multilingual = (detected_lang != "en")
    
    # Translate input to English if it is in a Bantu language
    processed_text = cleaned_text
    if is_multilingual:
        try:
            processed_text = GoogleTranslator(source=detected_lang, target="en").translate(cleaned_text)
        except Exception as e:
            print(f"Bantu translation error: {e}")

    text_lower = processed_text.lower()
    response = None

    # ---- 1. Math ----
    math_result, math_expr = extract_math(processed_text)
    if math_result is not None:
        response = f"**{math_expr} = {math_result}**"

    # ---- 2. Pronunciation ----
    if response is None:
        pronunciation_answer = handle_pronunciation(processed_text)
        if pronunciation_answer:
            # Pronunciation breakdown is inherently English-phonetic based, keep in English
            return pronunciation_answer

    # ---- 3. Hardcoded facts (direct, instant) ----
    if response is None:
        fact = lookup_fact(processed_text)
        if fact:
            response = fact

    # ---- 4. Language Capability Check ----
    if response is None:
        language_cap_pattern = r'\b(?:understand|speak|talk|write|translate|support|know|use)\s+([a-zA-Z\s-]+)'
        if re.search(language_cap_pattern, text_lower) or any(l in text_lower for l in ["zulu", "xhosa", "tsonga", "venda", "sepedi", "bantu"]):
            if any(phrase in text_lower for phrase in ["do you", "can you", "does the", "are you able to"]):
                response = (
                    "Yes, I fully understand and can communicate in South African languages including isiZulu, "
                    "isiXhosa, Xitsonga, Tshivenda, Sepedi, and others! You can chat with me in your language, "
                    "and I can translate your documents and read them aloud using localized accents."
                )

    # ---- 5. dakai / identity questions ----
    if response is None:
        identity_words = ["dakai", "dacai", "who are you", "what are you", "who made you",
                          "who created you", "who built you", "your name", "your creator",
                          "dac-technologies", "dac technologies", "your founders", "divine andiso cebo"]
        if any(phrase in text_lower for phrase in identity_words):
            if re.search(r'who\s+(are|is)\s+you|what\s+are\s+you', text_lower):
                response = (
                    "I'm dakai — your AI study partner built by dac-technologies, "
                    "a South African tech company founded in March 2026 by Divine, Andiso, and Cebo. "
                    "I help you read, understand, and learn from documents — plus I can answer questions, "
                    "do math, pronounce words, and translate into SA languages. What do you need?"
                )
            elif re.search(r'who\s+(created|made|built|founded)\s+you|your\s+(creator|developer|maker)', text_lower):
                response = (
                    "I was built by dac-technologies — a South African tech company "
                    "founded in March 2026 by Divine, Andiso, and Cebo. "
                    "The name 'dac' comes from their initials."
                )
            elif re.search(r'who\s+(are|is)\s+divine|andiso|cebo', text_lower):
                response = (
                    "Divine, Andiso, and Cebo are the co-founders of dac-technologies — "
                    "the South African company that built me. They started it in March 2026."
                )
            elif "dac-technologies" in text_lower or "dac technologies" in text_lower:
                response = (
                    "dac-technologies is a South African tech company founded in March 2026 "
                    "by Divine, Andiso, and Cebo. I'm their first product — an AI document reader and study partner."
                )

    # ---- 6. Greetings ----
    if response is None:
        if re.match(r'^(hi|hello|hey|sup|yo|howdy|heya|hiya)[\s!?]*$', text_lower):
            greets = [
                "Hey! I'm dakai — your AI study partner. Ask me anything, upload a document, or try some math!",
                "Hello! dakai here. What would you like to explore today?",
                "Hi there! Got a question, a document, or some math? Let's go.",
            ]
            response = random.choice(greets)

    # ---- 7. Capabilities ----
    if response is None:
        if re.search(r'what\s+can\s+you\s+do|how\s+do\s+you\s+work|your\s+(features|abilities)|what\s+is\s+your\s+(?:job|work|purpose|role)|what\s+do\s+you\s+do', text_lower):
            response = (
                "Here's what I can do:\n"
                "\u2022 Read & summarise documents (PDF, DOCX, TXT, images)\n"
                "\u2022 Answer factual questions directly\n"
                "\u2022 Do math — symbols or words ('2+2', '15 times 3')\n"
                "\u2022 Pronounce any word — 'how to pronounce [word]'\n"
                "\u2022 Translate documents into 10 South African languages\n"
                "\u2022 Read your document aloud with live highlighting"
            )

    # ---- 8. Document context ----
    if response is None:
        if context and len(context.strip()) > 50:
            doc_triggers = ['what does it say', 'summary', 'summarise', 'summarize', 'explain',
                            'tell me about', 'document', 'text', 'what is this', 'what is in']
            if any(t in text_lower for t in doc_triggers):
                sentences = re.split(r'(?<=[.!?])\s+', context.strip())
                preview = " ".join(sentences[:4])
                response = f"From your document: {preview[:500]}" + ("\u2026" if len(preview) > 500 else "")

    # ---- 9. Wikipedia ----
    if response is None:
        if is_knowledge_question(processed_text):
            wiki_answer = search_wikipedia(processed_text)
            if wiki_answer:
                _maybe_learn(processed_text, wiki_answer)
                response = wiki_answer

    # ---- 10. Learned Memory ----
    if response is None:
        words_in_input = set(re.split(r'\W+', text_lower))
        best_fact, best_score = None, 0
        for f in memory_store.get("learned_facts", []):
            keywords = set(f.get("keywords", []))
            required = f.get("required", [])
            if not keywords: continue
            overlap = len(words_in_input & keywords)
            if overlap == 0: continue
            if required and not all(r in words_in_input for r in required): continue
            score = overlap / len(keywords)
            if score > best_score:
                best_score, best_fact = score, f
        if best_fact and best_score > 0.4:
            response = best_fact["answer"]

    # ---- 11. Wellbeing ----
    if response is None:
        if re.search(r'how\s+are\s+you|how\s+do\s+you\s+feel|are\s+you\s+okay|how\s+is\s+it|hows\s+it|how\'s\s+it', text_lower):
            response = "I'm doing great, thanks for asking! How can I help you today?"

    # ---- 12. Goodbye ----
    if response is None:
        if re.search(r'^(bye|goodbye|see\s+you|later|cya|take\s+care)[\s!.]*$', text_lower):
            response = "Goodbye! Come back anytime you need a hand. \u2014 DACAI"

    # ---- 13. Last resort Wikipedia ----
    if response is None:
        wiki_attempt = search_wikipedia(processed_text)
        if wiki_attempt:
            _maybe_learn(processed_text, wiki_attempt)
            response = wiki_attempt

    # ---- 14. Graceful fallback ----
    if response is None:
        fallbacks = [
            "Hmm, I wasn't able to find a solid answer for that one. Could you rephrase or give me a bit more context? I want to get this right for you.",
            "That's a great question — I don't have enough info to answer it confidently right now. Try giving me more detail and I'll do my best.",
            "I'm not sure about that one yet. If you can add more context or rephrase, I'll take another shot at it.",
        ]
        response = random.choice(fallbacks)

    return translate_back_if_needed(response, active_lang)


# ----------------------------------------------------------------
# Self-learning
# ----------------------------------------------------------------
def _maybe_learn(user_input, ai_response):
    global memory_store
    if len(user_input) > 200 or len(ai_response) > 800:
        return
    keywords = [w.lower() for w in re.split(r'\W+', user_input) if len(w) > 3]
    if not keywords:
        return
    for fact in memory_store.get("learned_facts", []):
        if fact.get("question", "").lower() == user_input.lower():
            # Update existing fact
            fact["answer"] = ai_response
            save_memory(memory_store)
            return
    memory_store.setdefault("learned_facts", []).append({
        "question": user_input,
        "answer": ai_response,
        "keywords": keywords[:8],
        "required": keywords[:2],
    })
    if len(memory_store["learned_facts"]) > 500:
        memory_store["learned_facts"] = memory_store["learned_facts"][-500:]
    save_memory(memory_store)


# ----------------------------------------------------------------
# Translation
# ----------------------------------------------------------------
from translation_gateway import DakaiTranslationGateway

def safe_translate(text, target_lang):
    if not text:
        return ""
    try:
        max_chunk = 3000
        paragraphs = text.split("\n")
        chunks, current_chunk, current_len = [], [], 0
        for paragraph in paragraphs:
            if len(paragraph) > max_chunk:
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk, current_len = [], 0
                parts = re.split(r'([.!?]+\s+)', paragraph)
                temp_part, temp_len = [], 0
                for part in parts:
                    if temp_len + len(part) > max_chunk:
                        if temp_part: chunks.append("".join(temp_part))
                        temp_part, temp_len = [part], len(part)
                    else:
                        temp_part.append(part)
                        temp_len += len(part)
                if temp_part: chunks.append("".join(temp_part))
            else:
                if current_len + len(paragraph) + 1 > max_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk, current_len = [paragraph], len(paragraph)
                else:
                    current_chunk.append(paragraph)
                    current_len += len(paragraph) + 1
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        translated_parts = []
        for chunk in chunks:
            trimmed = chunk.strip()
            if trimmed:
                translated = asyncio.run(DakaiTranslationGateway.translate_document(trimmed, target_lang))
                translated_parts.append(translated)
            else:
                translated_parts.append(chunk)
        return "\n".join(translated_parts)
    except Exception as e:
        print(f"Translation error: {e}")
        from deep_translator import GoogleTranslator
        dt_lang = "ve" if target_lang in ["ven", "ve"] else target_lang
        return GoogleTranslator(source="auto", target=dt_lang).translate(text)


# ----------------------------------------------------------------
# Flask Routes
# ----------------------------------------------------------------
from enrichment import enrich_translation, get_available_dialects
from audio_mock import generate_word_timestamps, get_total_duration
from linguistics import XitsongaLinguisticRepair, get_sync_payload, DakaiInputLinguist, BanterIntent

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_input = data.get("message", "").strip()
    context = data.get("context", "")
    session_id = data.get("session_id", "default")
    target_lang = data.get("target_lang", None)

    if not user_input:
        return jsonify({"response": "Please type a message."})

    bot_response = build_response(user_input, context, session_id, target_lang)

    push_history(session_id, "user", user_input)
    push_history(session_id, "assistant", bot_response)

    return jsonify({"response": bot_response})


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.json or {}
        text = data.get("text", "")
        target_lang = data.get("target", "zu")
        translated = safe_translate(text, target_lang)
        return jsonify({"translatedText": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/translate-enriched", methods=["POST"])
def translate_enriched():
    """Translate + apply Bantu language enrichment pipeline and linguistic repairs."""
    try:
        data = request.json or {}
        text = data.get("text", "")
        target_lang = data.get("target", "zu")
        dialect = data.get("dialect", None)
        formality = float(data.get("formality", 0.5))

        # Step 1: Translate
        raw_translated = safe_translate(text, target_lang)

        # Step 2: Enrich (Bantu post-translation pipeline)
        enriched = enrich_translation(raw_translated, target_lang, dialect, formality)

        # Step 3: Apply grammatical/prefix repairs for Xitsonga
        if target_lang == "ts":
            enriched = XitsongaLinguisticRepair.repair_grammar(enriched)

        # Step 4: Generate sync/SSML metadata
        sync_data = get_sync_payload(enriched, target_lang)

        return jsonify({
            "translatedText": enriched,
            "rawTranslation": raw_translated,
            "language": target_lang,
            "dialect": dialect,
            "formality": formality,
            "enriched": True,
            "sync": sync_data
        })
    except Exception as e:
        print(f"Enriched translation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/audio-timestamps", methods=["POST"])
def audio_timestamps():
    """Generate mock word-level timestamps and phonetic/SSML sync payload."""
    try:
        data = request.json or {}
        text = data.get("text", "")
        speed = float(data.get("speed", 1.0))
        pitch = float(data.get("pitch", 1.0))
        lang = data.get("lang", "en")

        # Generate timestamps
        timestamps = generate_word_timestamps(text, speed, pitch)
        total_duration = get_total_duration(timestamps)

        # Generate dynamic audio-sync SSML payload
        sync_data = get_sync_payload(text, lang)

        return jsonify({
            "timestamps": timestamps,
            "total_duration": total_duration,
            "word_count": len(timestamps),
            "speed": speed,
            "pitch": pitch,
            "sync": sync_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/dialects", methods=["GET"])
def dialects():
    """Return available dialects for each language."""
    lang = request.args.get("lang", None)
    if lang:
        return jsonify({"language": lang, "dialects": get_available_dialects(lang)})
    # Return all
    all_dialects = {}
    for code in ["ts", "zu", "xh", "ve", "nso"]:
        all_dialects[code] = get_available_dialects(code)
    return jsonify(all_dialects)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "DACAI server running",
        "memory_facts": len(memory_store.get("learned_facts", [])),
        "active_sessions": len(sessions),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() in ["true", "1"]
    print(f"DACAI server starting on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
