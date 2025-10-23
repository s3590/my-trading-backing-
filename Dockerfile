# استخدم صورة بايثون الرسمية كنقطة بداية
FROM python:3.11-slim

# اضبط مجلد العمل داخل الحاوية
WORKDIR /app

# قم بتثبيت تبعيات النظام التي تحتاجها Pillow
# RUN تعني "نفّذ هذا الأمر أثناء بناء الصورة"
RUN apt-get update && apt-get install -y libjpeg-dev zlib1g-dev \
    # تنظيف مخلفات apt-get لتقليل حجم الصورة
    && rm -rf /var/lib/apt/lists/*

# انسخ ملف المتطلبات أولاً (للاستفادة من التخزين المؤقت لـ Docker)
COPY requirements.txt .

# قم بتثبيت مكتبات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# انسخ باقي ملفات المشروع إلى مجلد العمل
COPY . .

# حدد الأمر الذي سيتم تشغيله عند بدء تشغيل الحاوية
# لاحظ أننا نستخدم gunicorn هنا كما في إعدادات Render السابقة
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
