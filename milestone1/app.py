from flask import Flask, request, render_template
import pickle
import os

app = Flask(__name__)

for file in ["model.pkl", "vectorizer.pkl", "accuracy.pkl"]:
    if not os.path.exists(file):
        print(f"Missing {file}! Run 'python model.py' first.")
        exit()

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
accuracy = pickle.load(open("accuracy.pkl", "rb"))

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    real_percent = None
    fake_percent = None
    verdict = None
    input_news = ""

    if request.method == "POST":
        input_news = request.form.get("news", "")

        if input_news.strip() != "":
            news_vec = vectorizer.transform([input_news])
            prediction = model.predict(news_vec)[0]
            prob = model.predict_proba(news_vec)[0]

            classes = model.classes_
            real_idx = list(classes).index("REAL") if "REAL" in classes else 0
            fake_idx = list(classes).index("FAKE") if "FAKE" in classes else 1

            real_percent = round(prob[real_idx] * 100, 2)
            fake_percent = round(prob[fake_idx] * 100, 2)

            if prediction == "REAL":
                verdict = "The news is REAL "
            else:
                verdict = "The news is FAKE "

    return render_template(
        "index.html",
        prediction=prediction,
        real_percent=real_percent,
        fake_percent=fake_percent,
        accuracy=round(accuracy * 100, 2),
        verdict=verdict,
        input_news=input_news
    )

if __name__ == "__main__":
    app.run(debug=True)
