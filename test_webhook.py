import requests

# الرابط الخاص بك الذي يعمل عبر الإنترنت حالياً مع إضافة /webhook
url = "https://680e2649c1e788be-213-6-221-186.serveousercontent.com/webhook"

# رسالة تجريبية وهمية كأنها قادمة من الواتساب
payload = {
    "message": "أهلاً يا جيميناي، هل أنت جاهز للعمل؟"
}

print("جاري إرسال الطلب التجريبي إلى السيرفر...")
response = requests.post(url, json=payload)

print("\n--- رد السيرفر الفعلي ---")
print(response.json())