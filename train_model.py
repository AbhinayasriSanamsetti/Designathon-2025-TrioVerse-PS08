
import os
import cv2
import numpy as np
import pandas as pd
import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== TEXT DETECTION MODEL ====================

def train_text_model():
    print("Training text model...")
    
    fake_df = pd.read_csv(r"C:\Users\user\Downloads\archive (3)\News _dataset\Fake.csv")
    real_df = pd.read_csv(r"C:\Users\user\Downloads\archive (3)\News _dataset\True.csv")
    
    fake_df["label"] = 0  # Fake news
    real_df["label"] = 1  # Real news
    
    df = pd.concat([fake_df, real_df]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Missing 'text' or 'label' column! Ensure dataset has correct labels.")
    
    X = df["text"]
    y = df["label"]
    
    vectorizer = TfidfVectorizer()
    X_vectorized = vectorizer.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)
    
    text_model = MultinomialNB()
    text_model.fit(X_train, y_train)
    
    with open("text_model.pkl", "wb") as model_file:
        pickle.dump(text_model, model_file)
    
    with open("vectorizer.pkl", "wb") as vec_file:
        pickle.dump(vectorizer, vec_file)
    
    print("Text model training complete.")
    return text_model, vectorizer

text_model, vectorizer = train_text_model()

@app.route("/predict_text", methods=["POST"])
def predict_text():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400

        text_vector = vectorizer.transform([text])
        prediction = text_model.predict(text_vector)[0]
        confidence = round(max(text_model.predict_proba(text_vector)[0]) * 100, 2)

        return jsonify({"prediction": "Fake" if prediction == 0 else "Real", "confidence": confidence})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== IMAGE DETECTION MODEL ====================
@app.route("/predict_image", methods=["POST"])
def predict_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (100, 100)).flatten()

        is_fake = np.mean(img) < 127  

        return jsonify({"prediction": "Fake" if is_fake else "Real", "confidence": 75 if is_fake else 90})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== VIDEO DETECTION MODEL ====================
@app.route("/predict_video", methods=["POST"])
def predict_video():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        cap = cv2.VideoCapture(filepath)
        fake_count, total_frames = 0, 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray_frame)

            if avg_brightness < 127:
                fake_count += 1
            total_frames += 1

        cap.release()

        fake_percentage = round((fake_count / total_frames) * 100, 2) if total_frames > 0 else 0
        return jsonify({"prediction": "Fake" if fake_percentage > 50 else "Real", "confidence": fake_percentage})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
