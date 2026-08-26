import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_TOKEN = "d67zooznsqok1ia"
INSTANCE_ID = "instance189651"

# تهيئة المفتاح بالطريقة الكلاسيكية المستقرة
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


@app.route("/", methods=["GET"])
def home():
    return "Bot Server is running successfully!", 200


@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    print("--- WEBHOOK HIT ---")
    
    try:
        data = request.json
        if data and "data" in data:
            message_data = data["data"]
            sender = message_data.get("from")
            body = message_data.get("body")

            if message_data.get("fromMe"):
                return "OK", 200

            print(f"Processing message from {sender}: {body}")

            # توليد الرد بالطريقة المباشرة والمضمونة
            response = model.generate_content(body)
            reply_text = response.text
            print(f"Gemini reply: {reply_text}")

            url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
            payload = {
                "token": CLIENT_TOKEN,
                "to": sender,
                "body": reply_text,
                "priority": "10",
            }
            headers = {"content-type": "application/x-www-form-urlencoded"}
            
            api_response = requests.post(url, data=payload, headers=headers)
            print("UltraMsg Response:", api_response.text)

    except Exception as e:
        print("Error processing webhook:", e)

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)