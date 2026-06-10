import os
import hmac
import hashlib
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY        = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
ZERNIO_API_KEY        = os.environ.get("ZERNIO_API_KEY", "YOUR_ZERNIO_API_KEY")
ZERNIO_WEBHOOK_SECRET = os.environ.get("ZERNIO_WEBHOOK_SECRET", "")
GEMINI_MODEL          = "gemini-2.5-flash-lite"
GEMINI_URL            = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
ZERNIO_SEND_URL       = "https://api.zernio.com/v1/inbox/conversations/{conversation_id}/messages"

# ─── Scholarship Knowledge Base ────────────────────────────────────────────────
SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي لأكاديمية Learnova متخصص في الإجابة على أسئلة المنح الدراسية.
اللغة: العربية البسيطة الواضحة. كن ودودًا وموجزًا في ردودك.
أجب فقط بناءً على المعلومات التالية ولا تخترع معلومات غير موجودة:

--- معلومات المنح الدراسية ---
1. شروط التقديم: يجب أن يستوفي المتقدم المعدل الدراسي المطلوب، ومستوى الدخل المحدد، وتقديم جميع المستندات المطلوبة بشكل كامل.

2. معايير التقييم: تقييم الطلبات يتم بناءً على عدة معايير: GPA، مستوى الدخل، درجة الدافعية، اكتمال المستندات، ونتيجة المقابلة إن وجدت.

3. تعديل الطلب: يمكن تعديل البيانات قبل مرحلة المراجعة النهائية فقط. بعد بدء التقييم قد لا يكون التعديل متاحًا.

4. المستندات غير المكتملة: في حالة نقص المستندات قد يتم تأجيل الطلب أو رفضه. يُنصح برفع جميع المستندات المطلوبة بشكل كامل.

5. متابعة حالة الطلب: يمكن متابعة الحالة من خلال منصة Learnova. تُحدّث الحالة بشكل دوري: قيد المراجعة، مقبول، مرفوض.

6. التخصصات: يمكن التقديم من مختلف التخصصات، لكن يتم التفضيل حسب شروط كل منحة على حدة.

7. درجة الدافعية: تعكس مدى جدية المتقدم ورغبته في الحصول على المنحة. تُحدَّد من خلال نموذج التقديم أو المقابلة.

8. تأثير الدخل: في بعض المنح يُؤخذ مستوى الدخل في الاعتبار كعامل أساسي لتحديد الاستحقاق.

9. مدة المراجعة: تختلف حسب عدد الطلبات وتمر بعدة مراحل حتى يتم اتخاذ القرار النهائي.

10. في حالة الرفض: يمكن مراجعة سبب الرفض إن كان متاحًا، وتحسين البيانات أو التقديم في دفعات لاحقة إذا كانت المنحة تسمح بذلك.
---
إذا كان السؤال خارج نطاق المنح الدراسية، أخبر المستخدم بأدب أنك متخصص في المنح فقط وأرشده للتواصل مع الأكاديمية مباشرة."""


# ─── Signature Verification ────────────────────────────────────────────────────
def verify_signature(raw_body: bytes, signature: str) -> bool:
    if not ZERNIO_WEBHOOK_SECRET:
        return True
    expected = hmac.new(
        ZERNIO_WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


# ─── Gemini Call ───────────────────────────────────────────────────────────────
def ask_gemini(user_message: str) -> str:
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {"maxOutputTokens": 512, "temperature": 0.4}
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return "عذرًا، حدث خطأ مؤقت. حاول مرة أخرى."


# ─── Zernio Send Message ───────────────────────────────────────────────────────
def send_whatsapp_reply(conversation_id: str, text: str):
    url = ZERNIO_SEND_URL.format(conversation_id=conversation_id)
    headers = {
        "Authorization": f"Bearer {ZERNIO_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        print(f"[Zernio] Reply sent to conversation {conversation_id}")
    except Exception as e:
        print(f"[Zernio Error] {e}")


# ─── Webhook Endpoint ──────────────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    raw_body = request.get_data()

    sig = request.headers.get("X-Zernio-Signature", "")
    if ZERNIO_WEBHOOK_SECRET and not verify_signature(raw_body, sig):
        return jsonify({"error": "Invalid signature"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    event = data.get("event")
    print(f"[Webhook] Event: {event}")

    if event != "message.received":
        return jsonify({"ok": True}), 200

    message      = data.get("message", {})
    conversation = data.get("conversation", {})

    if message.get("fromMe"):
        return jsonify({"ok": True}), 200

    user_text       = message.get("text", "").strip()
    conversation_id = conversation.get("id", "")

    if not user_text or not conversation_id:
        return jsonify({"ok": True}), 200

    print(f"[Message] From conversation {conversation_id}: {user_text}")

    reply = ask_gemini(user_text)
    send_whatsapp_reply(conversation_id, reply)

    return jsonify({"ok": True}), 200


# ─── Health Check ──────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Learnova WhatsApp Bot is running ✓"}), 200
