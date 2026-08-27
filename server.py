import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)

# ==================== إعداد جيميني ====================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

INSTANCE_ID = "instance189651"

# ==================== ملف حفظ المواعيد الجديدة ====================
APPOINTMENTS_FILE = "appointments.json"

def load_appointments():
    if os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_appointment(name, date, time, note=""):
    appointments = load_appointments()
    appointments.append({
        "name": name,
        "date": date,
        "time": time,
        "note": note,
        "created_at": datetime.now().isoformat()
    })
    with open(APPOINTMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(appointments, f, ensure_ascii=False, indent=2)
    return appointments[-1]

# ==================== تعريف الأداة (Function) اللي الموديل يقدر يستدعيها ====================
book_appointment_function = genai.protos.FunctionDeclaration(
    name="book_appointment",
    description="يحجز موعد جديد مع المهندس محمد ضهير عندما يوافق العميل على وقت محدد ضمن أوقات التواصل مع العملاء (2 إلى 4 مساءً).",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "name": genai.protos.Schema(type=genai.protos.Type.STRING, description="اسم العميل"),
            "date": genai.protos.Schema(type=genai.protos.Type.STRING, description="تاريخ الموعد، مثل: غداً أو 30-08-2026"),
            "time": genai.protos.Schema(type=genai.protos.Type.STRING, description="وقت الموعد، مثل: 3:00 مساءً"),
            "note": genai.protos.Schema(type=genai.protos.Type.STRING, description="ملاحظة مختصرة عن سبب التواصل/الطلب"),
        },
        required=["name", "date", "time"]
    )
)

tools = genai.protos.Tool(function_declarations=[book_appointment_function])

# ==================== شخصية وتعليمات البوت ====================
SYSTEM_PROMPT = """
أنت "مستشار برلين"، الوكيل الذكي الذي يرد نيابة عن المهندس محمد ضهير (Mohammed Dhaher).
لا تقدّم نفسك أبداً باسم المهندس محمد، بل دائماً باسم "مستشار برلين" ووضّح أنك تتحدث نيابةً عنه عند الحاجة.

معلومات عن المهندس محمد ضهير (لا تشاركها كاملة إلا عند الحاجة):
- مهندس ومبرمج ومصمم تطبيقات موبايل، متخصص Flutter Developer بخبرة تفوق 5 سنوات.
- يعمل مستقلاً (فريلانسر) على منصات مثل Upwork وFreelancer ومستقل وغيرها.

جدول المهندس محمد اليومي (استخدمه لمعرفة إذا كان متاحاً أو مشغولاً وقت معين):
- 8:00 - 9:00 صباحاً: تمرين رياضي (غير متاح)
- 9:00 - 10:00 صباحاً: فطور (غير متاح)
- 10:00 صباحاً - 2:00 مساءً: يعمل على تطوير مشاريعه الخاصة (غير متاح للرد المباشر إلا لو الأمر عاجل جداً)
- 2:00 - 4:00 مساءً: وقت مخصص للرد على العملاء والاستفسارات والمواعيد الجديدة (هذا هو الوقت المتاح للحجز)
- 5:00 - 8:00 مساءً: نزهة على البحر (غير متاح)
- بعد 8:00 مساءً: صلاة المغرب والعشاء ووقت مع العائلة (غير متاح)

قواعد الرد:
- إذا سألك أحد "هل هو متاح الآن؟" أو عن وقت معين، أجب بصدق بناءً على الجدول أعلاه دون كشف كل التفاصيل الشخصية (فقط قل مثلاً: "المهندس محمد غير متاح حالياً، هو متاح للرد على الاستفسارات من الساعة 2 حتى 4 مساءً").
- إذا أراد العميل حجز موعد ضمن وقت التواصل مع العملاء (2-4 مساءً)، اجمع اسمه والوقت المطلوب، ثم استخدم أداة book_appointment لتسجيل الحجز فعلياً، وأكّد له ذلك بوضوح.
- لا تحجز مواعيد خارج وقت 2-4 مساءً؛ إذا طلب وقتاً آخر، اقترح عليه بلطف أقرب وقت متاح ضمن 2-4 مساءً.

أسلوب الكتابة (مهم جداً):
- اكتب بأسلوب احترافي راقٍ يليق بمهندس ومطوّر تطبيقات ذي خبرة، بحيث يشعر العميل بالثقة والاهتمام من أول رسالة.
- استخدم عبارات ترحيب وتقدير لطيفة (مثل شكر العميل على تواصله)، وصياغة مرتبة وواضحة، مع تجنب الجمل الجافة أو المقتضبة جداً.
- نظّم الرد إذا كان يحتوي معلومات متعددة (نقاط أو أسطر منفصلة) بدل حشرها بجملة واحدة طويلة.
- حافظ على اللغة العربية الفصحى المبسطة أو لهجة مهذبة راقية، وتجنب العامية الدارجة الزائدة.
- اختم الرسائل المهمة (كالتأكيد على موعد) بعبارة ودّية تُشعر العميل بالاهتمام، دون مبالغة أو إطالة غير ضرورية.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
    tools=[tools]
)

# ==================== ذاكرة المحادثات ====================
chat_sessions = {}

def get_chat_session(sender):
    if sender not in chat_sessions:
        chat_sessions[sender] = model.start_chat(history=[])
    return chat_sessions[sender]


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

        chat = get_chat_session(sender)
        response = chat.send_message(text)

        # تحقق إذا الموديل طلب تنفيذ أداة (حجز موعد)
        reply_text = ""
        for part in response.parts:
            if part.function_call and part.function_call.name == "book_appointment":
                args = part.function_call.args
                appt = save_appointment(
                    name=args.get("name", sender),
                    date=args.get("date", ""),
                    time=args.get("time", ""),
                    note=args.get("note", "")
                )
                print(f"Appointment saved: {appt}")

                # نرجع نتيجة تنفيذ الأداة للموديل عشان يصيغ رد نهائي للعميل
                follow_up = chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name="book_appointment",
                                response={"status": "success", "appointment": appt}
                            )
                        )]
                    )
                )
                reply_text = follow_up.text
            elif part.text:
                reply_text += part.text

        if not reply_text:
            reply_text = "تم استلام رسالتك، سأقوم بالرد قريباً."

        print(f"Reply: {reply_text}")

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