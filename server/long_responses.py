import random

R_ADVICE = (
    "Here are some solid study tips: Break your material into small chunks and tackle one section at a time. "
    "Use the dacai reader to listen to your documents while reading along \u2014 this dual input boosts retention. "
    "Review summaries after each session, and teach the concepts back to yourself out loud."
)

R_DOCUMENT_TIPS = (
    "To get the most out of dacai: Upload your PDF, DOCX, TXT, or image file using the upload button. "
    "The reader will highlight each sentence as it reads aloud. You can click any sentence to jump to it, "
    "adjust reading speed, and translate the full document into any South African language."
)

UNKNOWN_RESPONSES = [
    "I'm not sure I understood that. Could you rephrase or give me more detail?",
    "Hmm, that's a tricky one. Try asking me differently or give me a document to work with.",
    "I don't have a clear answer for that yet \u2014 but I'm always learning! Try rephrasing.",
    "I'm still growing my knowledge. Could you ask that in a different way?",
    "That's outside what I currently know well. Can you give me more context?",
]

def unknown():
    return random.choice(UNKNOWN_RESPONSES)
