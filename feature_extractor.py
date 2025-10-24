import cv2
import numpy as np
import pytesseract
import pandas as pd
from PIL import Image
import os

# --- Configuration (Based on typical Pocket Option Mobile Screenshot) ---
# Normalized coordinates (0 to 1000) for robustness
CHART_ROI_NORMALIZED = [50, 150, 950, 850] # Main chart area
PRICE_ROI_NORMALIZED = [850, 50, 1000, 150] # Area for price/asset name
TIME_ROI_NORMALIZED = [50, 50, 200, 100] # Area for time frame/expiry

# --- Color Definitions (Pocket Option) ---
# Green (Up) - HSV
GREEN_LOWER = np.array([40, 40, 40])
GREEN_UPPER = np.array([80, 255, 255])

# Red (Down) - HSV (Using two ranges for red since it wraps around 0 in HSV)
RED_LOWER1 = np.array([0, 40, 40])
RED_UPPER1 = np.array([170, 255, 255]) # Adjusted to cover a wider range for red

def normalize_and_crop(img, normalized_roi):
    """Crops the image based on normalized ROI."""
    h, w, _ = img.shape
    x_min = int(normalized_roi[0] * w / 1000)
    y_min = int(normalized_roi[1] * h / 1000)
    x_max = int(normalized_roi[2] * w / 1000)
    y_max = int(normalized_roi[3] * h / 1000)
    return img[y_min:y_max, x_min:x_max]

def extract_ocr_features(img):
    """Extracts text features using OCR."""
    price_roi = normalize_and_crop(img, PRICE_ROI_NORMALIZED)
    time_roi = normalize_and_crop(img, TIME_ROI_NORMALIZED)
    
    # Preprocess for OCR (grayscale and thresholding)
    price_gray = cv2.cvtColor(price_roi, cv2.COLOR_BGR2GRAY)
    _, price_thresh = cv2.threshold(price_gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    time_gray = cv2.cvtColor(time_roi, cv2.COLOR_BGR2GRAY)
    _, time_thresh = cv2.threshold(time_gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Use OCR
    price_text = pytesseract.image_to_string(price_thresh, config='--psm 6').strip()
    time_text = pytesseract.image_to_string(time_thresh, config='--psm 6').strip()
    
    # Simple feature: presence of text (can be expanded to clean and convert to float)
    return {
        'price_text_present': 1 if price_text else 0,
        'time_text_present': 1 if time_text else 0,
        'ocr_price': price_text, # Keep for debugging/future use
        'ocr_time': time_text    # Keep for debugging/future use
    }

def extract_candlestick_features(img):
    """Analyzes the chart area to extract candlestick patterns and trend features."""
    chart_roi = normalize_and_crop(img, CHART_ROI_NORMALIZED)
    hsv_chart = cv2.cvtColor(chart_roi, cv2.COLOR_BGR2HSV)
    
    # Create masks for green and red candles
    mask_green = cv2.inRange(hsv_chart, GREEN_LOWER, GREEN_UPPER)
    mask_red = cv2.inRange(hsv_chart, RED_LOWER1, RED_UPPER1)
    
    # --- Feature 1: Candle Counts (Simple Trend/Momentum) ---
    green_pixels = np.sum(mask_green > 0)
    red_pixels = np.sum(mask_red > 0)
    total_pixels = chart_roi.size // 3
    
    green_ratio = green_pixels / total_pixels
    red_ratio = red_pixels / total_pixels
    
    # --- Feature 2: Last Candle Color/Momentum (Focus on the rightmost 10%) ---
    last_candle_area = chart_roi[:, int(chart_roi.shape[1] * 0.9):]
    hsv_last = cv2.cvtColor(last_candle_area, cv2.COLOR_BGR2HSV)
    
    mask_last_green = cv2.inRange(hsv_last, GREEN_LOWER, GREEN_UPPER)
    mask_last_red = cv2.inRange(hsv_last, RED_LOWER1, RED_UPPER1)
    
    last_green_pixels = np.sum(mask_last_green > 0)
    last_red_pixels = np.sum(mask_last_red > 0)
    
    # --- Feature 3: Simple Trend (Difference in pixel ratios) ---
    trend_score = green_ratio - red_ratio
    
    # --- Feature 4: Volatility (based on total colored pixels) ---
    volatility = (green_pixels + red_pixels) / total_pixels

    return {
        'green_ratio': green_ratio,
        'red_ratio': red_ratio,
        'trend_score': trend_score,
        'volatility': volatility,
        'last_candle_is_green': 1 if last_green_pixels > last_red_pixels * 1.5 else 0,
        'last_candle_is_red': 1 if last_red_pixels > last_green_pixels * 1.5 else 0,
    }

def extract_features_from_image(image_data):
    """Main function to extract all features from base64 image data."""
    # Decode the base64 string
    image_data = image_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Could not decode image data.")
        
    ocr_features = extract_ocr_features(img)
    candlestick_features = extract_candlestick_features(img)
    
    # Combine features
    all_features = {**ocr_features, **candlestick_features}
    
    # Extract only the features used for training
    feature_names = [
        'price_text_present', 'time_text_present',
        'green_ratio', 'red_ratio', 'trend_score',
        'volatility', 'last_candle_is_green', 'last_candle_is_red'
    ]
    
    # Create a list of feature values in the correct order for the model
    features_vector = [all_features[name] for name in feature_names]
    
    return features_vector

if __name__ == '__main__':
    # This block is for testing the function locally if needed
    pass
