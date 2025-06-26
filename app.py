# app.py
# ----------------------------
# Flask + ML Model + HTML UI + JSON API
# ----------------------------
from flask import Flask, request, jsonify, render_template
import pickle
import os

app = Flask(__name__)

# ---------- 1. मॉडल लोड ----------
MODEL_PATH = "flower_model.pkl"
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# ---------- 2. हेल्पर : रंग को नम्बर में बदलें ----------
COLOR_MAP = {"हरा": 0, "लाल": 1, "पीला": 2}
def color_to_number(color_name: str) -> int:
    return COLOR_MAP.get(color_name.strip().lower(), -1)

# ---------- 3. HTML होमपेज (GET) + फ़ॉर्म प्रिडिक्शन (POST) ----------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        color = request.form.get("color", "")
        size  = request.form.get("size", "")
        try:
            color_val = color_to_number(color)
            size_val  = int(size)
            if color_val == -1 or not 1 <= size_val <= 10:
                result = "⚠️ सही रंग (हरा/लाल/पीला) व आकार (1-10) दें!"
            else:
                pred = model.predict([[color_val, size_val]])[0]
                result = "🌸 यह फूल है!" if pred == 1 else "🌿 यह खरपतवार है!"
        except Exception:
            result = "⚠️ इनपुट फ़ॉर्मेट गलत है!"
    return render_template("index.html", result=result)

# ---------- 4. JSON API ---------- 
#    POST /predict
#    Body: { "color": "हरा", "size": 5 }
#    Response: { "prediction": "फूल है!" }
@app.route("/predict", methods=["POST"])
def api_predict():
    if not request.is_json:
        return jsonify({"error": "JSON body expected"}), 415

    data = request.get_json(silent=True) or {}
    color = data.get("color")
    size  = data.get("size")

    # बेसिक वैलिडेशन
    if color is None or size is None:
        return jsonify({"error": "Both 'color' and 'size' needed"}), 400

    color_val = color_to_number(color)
    if color_val == -1:
        return jsonify({"error": "Allowed colors: हरा, लाल, पीला"}), 400
    try:
        size_val = int(size)
    except (TypeError, ValueError):
        return jsonify({"error": "'size' must be integer"}), 400
    if not 1 <= size_val <= 10:
        return jsonify({"error": "size must be 1-10"}), 400

    # प्रिडिक्शन
    try:
        pred = model.predict([[color_val, size_val]])[0]
        label = "फूल है!" if pred == 1 else "खरपतवार है!"
        return jsonify({"prediction": label})
    except Exception as e:
        # फ़ॉलबैक – कोई अनपेक्षित त्रुटि
        return jsonify({"error": str(e)}), 500

# ---------- 5. एंट्री-पॉइंट ----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))   # Render PORT env var
    app.run(host="0.0.0.0", port=port, debug=True)