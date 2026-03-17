from flask import Flask, render_template, request
import spacy
import re

app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    tokens = []
    lemmas = []
    entities = []
    cleaned_text = ""

    if request.method == "POST":
        text = request.form["text"]

        doc = nlp(text)

        tokens = [token.text for token in doc]
        lemmas = [token.lemma_ for token in doc]
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        cleaned_text = clean_text(text)

    return render_template(
        "index.html",
        tokens=tokens,
        lemmas=lemmas,
        entities=entities,
        cleaned_text=cleaned_text
    )

if __name__ == "__main__":
    app.run(debug=True)