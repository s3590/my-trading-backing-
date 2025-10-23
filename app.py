import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

app = Flask(__name__)
CORS(app)

# تحميل النموذج عند بدء تشغيل الخادم
# The model file 'trading_model.h5' must be in the same directory
try:
    model = load_model('trading_model.h5')
    print("Model loaded successfully!")
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

def prepare_image(image_data):
    """Decodes image from base64, resizes and prepares it for the model."""
    # Decode the base64 string
    image_data = base64.b64decode(image_data.split(',')[1])
    # Open the image
    image = Image.open(io.BytesIO(image_data)).convert('RGB')
    # Resize to the target size the model expects (e.g., 224x224)
    image = image.resize((224, 224))
    # Convert image to array
    image = img_to_array(image)
    # Expand dimensions to match the model's input shape
    image = np.expand_dims(image, axis=0)
    # Normalize the image data
    image = image / 255.0
    return image

@app.route('/analyze-dual', methods=['POST'])
def analyze_dual_image():
    if not model:
        return jsonify({"error": "Model is not loaded. Check server logs."}), 500

    data = request.get_json()
    if not data or 'image_m5' not in data:
        return jsonify({"error": "الرجاء إرسال صورة التحليل"}), 400

    try:
        # We only need one image for our custom model
        image_data = data['image_m5']
        
        # Prepare the image for the model
        prepared_image = prepare_image(image_data)
        
        # Make prediction
        prediction = model.predict(prepared_image)
        
        # The output of the model is a probability. 
        # If it's > 0.5, it's 'Up' (class 1), otherwise it's 'Down' (class 0)
        if prediction[0][0] > 0.5:
            final_result = "صعود"
        else:
            final_result = "هبوط"
            
        return jsonify({"prediction": final_result})

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({"error": "فشل تحليل الصورة"}), 500

@app.route('/')
def index():
    return "خادم التحليل بالنموذج المخصص يعمل الآن!"

# The following is needed for Render to run the app
if __name__ == '__main__':
    # Render dynamically assigns a port, so we use the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
