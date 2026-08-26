import os
import requests
from flask import Flask, request

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_TOKEN = "d67zooznsqok1ia"
INSTANCE_ID = "instance189651"


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

            # الاتصال المباشر برتست API الخاص بجوجل لتجاوز جميع مشاكل المكتبات
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            
            gemini_payload = {
                "contents": [{
                    "parts": [{"text": body}]
                }]
            }
            
            gemini_res = requests.post(gemini_url, json=gemini_payload)
            gemini_data = gemini_res.json()
            
            print("Gemini API Raw Response:", gemini_data)

            # استخراج الرد بدقة تامة
            try:
                reply_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                reply_text = "أهلاً بك، وصلتني رسالتك ولكن حدث خطأ بسيط في معالجة الرد."

            print(f"Gemini reply: {reply_text}")

            # إرسال الرد عبر UltraMsg للواتساب
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