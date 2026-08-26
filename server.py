import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)

# إعداد مفتاح جيميني
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# استخدام موديل مستقر ومضمون
model = genai.GenerativeModel('gemini-pro')

INSTANCE_ID = "instance189651" 

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "OK", 200

    print("--- WEBHOOK HIT ---")
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    try:
        message_data = data.get("data", {})
        
        if message_data.get("fromMe", False):
            return "OK", 200

        sender = message_data.get("from", "")
        text = message_data.get("body", "")

        if not sender or not text:
            return "OK", 200

        print(f"Processing message from {sender}: {text}")

        # توليد الرد من جيميني
        response = model.generate_content(text)
        reply_text = response.text
        print(f"Gemini reply: {reply_text}")

        # إرسال الرد عبر UltraMsg باستخدام التوكن من الـ Environment
        token = os.environ.get("ULTRAMSG_TOKEN")
        url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
        payload = {
            "token": token,
            "to": sender,
            "body": reply_text
        }
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        
        r = requests.post(url, data=payload, headers=headers)
        print("UltraMsg Response:", r.text)

    except Exception as e:
        print(f"Error processing webhook: {e}")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))