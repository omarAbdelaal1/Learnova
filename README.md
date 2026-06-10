# Learnova WhatsApp Chatbot — دليل النشر على Vercel

## المتطلبات
- Zernio account مع رقم واتساب متصل
- Gemini API Key من https://aistudio.google.com/apikey
- Vercel account (مجاني) من https://vercel.com

---

## هيكل الملفات

```
learnova-bot/
├── api/
│   └── index.py        ← الكود الأساسي (serverless function)
├── requirements.txt    ← المكتبات
├── vercel.json         ← إعدادات Vercel
└── README.md
```

---

## الخطوة 1 — رفع الكود على GitHub

1. أنشئ repo جديد على GitHub
2. ارفع محتويات هذا الفولدر فيه

---

## الخطوة 2 — النشر على Vercel

1. اذهب إلى https://vercel.com → **Add New Project**
2. اربطه بالـ repo من GitHub
3. اضغط **Deploy** (Vercel يكتشف الإعدادات تلقائيًا من `vercel.json`)

4. بعد الـ deploy، أضف **Environment Variables** من:
   `Project Settings → Environment Variables`

   ```
   GEMINI_API_KEY          = AIza...
   ZERNIO_API_KEY          = your_zernio_key
   ZERNIO_WEBHOOK_SECRET   = (اختياري)
   ```

5. بعد إضافة المتغيرات، اعمل **Redeploy** من لوحة التحكم.

6. هتاخد URL زي:
   `https://learnova-bot.vercel.app`

---

## الخطوة 3 — ربط الـ Webhook في Zernio

1. اذهب إلى Zernio Dashboard → Webhooks → Create
2. الإعدادات:
   - **URL:** `https://learnova-bot.vercel.app/webhook`
   - **Events:** ✅ `message.received`
   - **Secret:** أي كلمة سر (نفسها في ZERNIO_WEBHOOK_SECRET)
3. احفظ وابعت Test — المفروض يجيلك `{"ok": true}`

---

## الخطوة 4 — اختبار

ابعت رسالة واتساب على الرقم المتصل بـ Zernio وانتظر الرد!

---

## مميزات Vercel مقارنةً بـ Render

| الميزة | Vercel | Render (Free) |
|--------|--------|---------------|
| Cold start | لا يوجد | 30 ثانية بعد خمول |
| الاستجابة | سريعة جدًا (serverless) | بطيئة أحيانًا |
| الخطة المجانية | سخية | محدودة |
| مناسب لـ Webhooks | ✅ ممتاز | ⚠️ مشكلة الخمول |

---

## ملاحظة مهمة
Vercel serverless functions لها حد زمني **10 ثوانٍ** على الخطة المجانية.
الكود الحالي يعمل ضمن هذا الحد بشكل طبيعي.
