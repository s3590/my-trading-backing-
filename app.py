import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64
import joblib # For loading the scikit-learn model
import cv2 # For image processing in feature extraction
import pytesseract # For OCR in feature extraction
from feature_extractor import extract_features_from_image # Import the feature extraction logic

# --- Configuration ---
MODEL_FILENAME = 'trading_model.joblib'

app = Flask(__name__)
CORS(app)

# تحميل النموذج عند بدء تشغيل الخادم
try:
    # Load the scikit-learn model
    model = joblib.load(MODEL_FILENAME)
    print("Model loaded successfully!")
except Exception as e:
    model = None
    print(f"Error loading model: {e}. Make sure {MODEL_FILENAME} is in the same directory.")

# The prepare_image function is no longer needed as the feature extractor handles decoding and processing.

@app.route('/analyze-dual', methods=['POST'])
def analyze_dual_image():
    if not model:
        return jsonify({"error": "Model is not loaded. Check server logs."}), 500

    data = request.get_json()
    if not data or 'image_m5' not in data:
        return jsonify({"error": "الرجاء إرسال صورة التحليل"}), 400

    try:
        # The frontend sends the image data as a base64 string
        image_data = data['image_m5']
        
        # 1. Extract features from the raw image data
        # This function handles decoding, OCR, and candlestick analysis
        features_vector = extract_features_from_image(image_data)
        
        # 2. Prepare the features for the model
        # The model expects a 2D array (e.g., [[feature1, feature2, ...]])
        prepared_features = np.array([features_vector])
        
        # 3. Make prediction
        prediction = model.predict(prepared_features)[0]
        
        # 4. Convert prediction (0 or 1) to result
        if prediction == 1:
            final_result = "صعود"
        else:
            final_result = "هبوط"
            
        return jsonify({"prediction": final_result})

    except Exception as e:
        print(f"Prediction Error: {e}")
        # Return a more informative error for the user
        return jsonify({"error": f"فشل تحليل الصورة. الخطأ: {str(e)}"}), 500

@app.route('/')
def index():
    return "خادم تحليل التداول بالنموذج المتقدم يعمل الآن!"

# The following is needed for Render to run the app
if __name__ == '__main__':
    # Render dynamically assigns a port, so we use the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
