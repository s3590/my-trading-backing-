# استخدم صورة بايثون الرسمية كنقطة بداية
FROM python:3.11-slim

# اضبط مجلد العمل داخل الحاوية
WORKDIR /app

# انسخ ملف المتطلبات أولاً (للاستفادة من التخزين المؤقت لـ Docker)
COPY requirements.txt .

# قم بتثبيت تبعيات النظام التي تحتاجها Pillow و Tesseract OCR و OpenCV
RUN apt-get update && \
    apt-get install -y libjpeg-dev zlib1g-dev \
    # تبعيات OpenCV (لحل مشكلة libGL.so.1)
    libgl1-mesa-glx libsm6 libxext6 libxrender-dev \
    # تبعيات Tesseract
    tesseract-ocr libtesseract-dev \
    # تنظيف مخلفات apt-get لتقليل حجم الصورة
    && rm -rf /var/lib/apt/lists/*

# قم بتثبيت مكتبات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# انسخ باقي ملفات المشروع إلى مجلد العمل (الآن بعد تثبيت المكتبات)
COPY . .

# حدد الأمر الذي سيتم تشغيله عند بدء تشغيل الحاوية
# لاحظ أننا نستخدم gunicorn هنا كما في إعدادات Render السابقة
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
