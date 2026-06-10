# Learnova WhatsApp Chatbot — دليل التشغيل

## المتطلبات
- Zernio account (Usage plan) مع رقم واتساب متصل
- Gemini API Key من https://aistudio.google.com/apikey
- Render.com account (مجاني)

---

## الخطوة 1 — رفع الكود على Render

1. ارفع هذا الفولدر على GitHub (repo جديد أو خاص)
2. اذهب إلى https://render.com → New → Web Service
3. اربطه بالـ repo
4. الإعدادات:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app --bind 0.0.0.0:$PORT`
   - **Plan:** Free

5. أضف Environment Variables:
   ```
   GEMINI_API_KEY     = AIza...
   ZERNIO_API_KEY     = your_zernio_key
   ZERNIO_WEBHOOK_SECRET = (اختياري، من Zernio dashboard)
   ```

6. بعد الـ deploy، هتاخد URL زي:
   `https://learnova-bot.onrender.com`

---

## الخطوة 2 — ربط الـ Webhook في Zernio

1. اذهب إلى Zernio Dashboard → Webhooks → Create
2. الإعدادات:
   - **URL:** `https://learnova-bot.onrender.com/webhook`
   - **Events:** ✅ `message.received`
   - **Secret:** أي كلمة سر (نفسها في ZERNIO_WEBHOOK_SECRET)
3. احفظ وابعت Test — المفروض يجيلك `{"ok": true}`

---

## الخطوة 3 — اختبار

ابعت رسالة واتساب على الرقم المتصل بـ Zernio وانتظر الرد!

---

## ملاحظات مهمة
- Render Free tier بينام بعد 15 دقيقة خمول → أول رسالة ممكن تاخد 30 ثانية
- للإنتاج الحقيقي: استخدم Render Starter ($7/شهر) أو Railway
- الـ 24-hour window: لو العميل ماكلمكش من 24 ساعة، لازم تبدأ بـ template message
