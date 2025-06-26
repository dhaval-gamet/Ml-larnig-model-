from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# 🔹  मॉडल लोड करें
with open("flower_model.pkl", "rb") as f:
    model = pickle.load(f)

# 🔹  कलर-नाम को नम्बर में बदलने वाला फ़ंक्शन
def color_to_number(name):
    name = name.strip().lower()
    mapping = {"हरा": 0, "लाल": 1, "पीला": 2}
    return mapping.get(name, -1)

# 🔹  होम पेज (GET) + प्रिडिक्शन (POST)
@app.route("/", methods=["GET", "POST"])
def index():
    prediction_text = None
    if request.method == "POST":
        color = request.form.get("color", "")
        size  = request.form.get("size", "")
        try:
            color_num = color_to_number(color)
            size_int  = int(size)

            if color_num == -1 or not (1 <= size_int <= 10):
                prediction_text = "⚠️ सही रंग (हरा/लाल/पीला) व साइज (1-10) दें!"
            else:
                pred = model.predict([[color_num, size_int]])[0]
                prediction_text = "🌸 यह फूल है!" if pred == 1 else "🌿 यह खरपतवार है!"
        except:
            prediction_text = "⚠️ इनपुट फ़ॉर्मेट गलत है!"

    return render_template("index.html", result=prediction_text)

# 🔹  Replit/Render के लिए पोर्ट सेट-अप
if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
