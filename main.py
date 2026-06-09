import re
import long_responses as long
from PIL import Image
import pytesseract
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow requests from your HTML frontend

# ---------------- Chatbot Core ----------------
def message_probability(user_message, recognised_words, single_response=False, required_words=[]):
    message_certainty = 0
    has_required_words = True

    for word in user_message:
        if word in recognised_words:
            message_certainty += 1

    percentage = float(message_certainty) / float(len(recognised_words))

    for word in required_words:
        if word not in user_message:
            has_required_words = False
            break

    if has_required_words or single_response:
        return int(percentage * 100)
    else:
        return 0


def check_all_messages(message):
    highest_prob_list = {}

    def response(bot_response, list_of_words, single_response=False, required_words=[]):
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = message_probability(
            message, list_of_words, single_response, required_words
        )

    response('Hello!', ['hello', 'hi', 'hey', 'sup', 'heyo', 'yo'], single_response=True)
    response('See you!', ['bye', 'goodbye'], single_response=True)
    response('I am doing fine, and you?', ['how', 'are', 'you', 'doing'], required_words=['how'])
    response(long.R_ADVICE, ['give', 'advice'], required_words=['advice'])
    #response(long_read,['read','please'],single_response=True)

    best_match = max(highest_prob_list, key=highest_prob_list.get)
    return long.unknown() if highest_prob_list[best_match] < 1 else best_match


def get_response(user_input):
    split_message = re.split(r'\s+|[,;?!.-]\s*', user_input.lower())
    response = check_all_messages(split_message)
    return response


def scan_image(image_path):
    try:
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)
        return extracted_text.strip()
    except Exception as e:
        return f"Error scanning image: {e}"


# ---------------- Flask API ----------------
@app.route("/chat", methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message", "")
    bot_response = get_response(user_input)
    return jsonify({"response": bot_response})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
