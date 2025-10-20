import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
app = Flask(__name__)
CORS(app)
# !!! هام: سنقوم بوضع المفتاح الخاص بك هنا لاحقًا
client = OpenAI(api_key="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")
DUAL_PROMPT_TEXT = "أنت محلل فني خبير، مهمتك هي تحديد فرص التداول عالية الاحتمالية من خلال مقارنة إطارين زمنيين. سأعطيك صورتين لنفس الأصل: M5 و M15. 1. تحليل الاتجاه العام (صورة M15): انظر إلى شارت الـ 15 دقيقة لتحديد الاتجاه الرئيسي للسوق. هل هو صاعد، هابط، أم عرضي؟ حدد أي مستويات دعم أو مقاومة قوية وواضحة. 2. تحليل نقطة الدخول والزخم (صورة M5): انظر الآن إلى شارت الـ 5 دقائق. هل حركة السعر الحالية في M5 تتوافق مع الاتجاه العام الذي حددته من M15؟ ابحث عن أي نماذج شموع تأكيدية على شارت M5 تدعم هذا الاتجاه. 3. القرار النهائي: بناءً على مدى توافق التحليل بين الإطارين، ما هو التوقع الأكثر ترجيحًا للحركة القادمة؟ 4. أجب بكلمة واحدة فقط: 'صعود' أو 'هبوط'."
@app.route('/analyze-dual', methods=['POST'])
def analyze_dual_image():
    data = request.get_json()
    if not data or 'image_m5' not in data or 'image_m15' not in data:
        return jsonify({"error": "الرجاء إرسال الصورتين (M5 و M15)"}), 400
    image_m5_url = data['image_m5']
    image_m15_url = data['image_m15']
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": DUAL_PROMPT_TEXT},
                    {"type": "image_url", "image_url": {"url": image_m15_url, "detail": "low"}},
                    {"type": "image_url", "image_url": {"url": image_m5_url, "detail": "high"}},
                ]}
            ], max_tokens=10)
        analysis_result = response.choices[0].message.content.strip().lower()
        if "صعود" in analysis_result: final_result = "صعود"
        elif "هبوط" in analysis_result: final_result = "هبوط"
        else: final_result = "غير محدد"
        return jsonify({"prediction": final_result})
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return jsonify({"error": "فشل تحليل الصورة"}), 500
@app.route('/')
def index():
    return "خادم التحليل الاحترافي يعمل!"
# The following is needed for Render to run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    