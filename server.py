import os
from flask import Flask, request
from google import genai

# تعريف تطبيق Flask بالاسم app تماماً لتتوافق مع Gunicorn
app = Flask(__name__)

# استدعاء مفتاح جيميناي بأمان من متغيرات البيئة في Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


@app.route("/", methods=["GET"])
def home():
  return "Bot Server is running successfully!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
  data = request.json
  # هنا يمكنك استقبال رسائل الواتساب ومعالجتها عبر جيميناي
  # سيتم ربط رسائل الواتساب وردود البوت هنا
  print("Received data:", data)
  return "OK", 200


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)