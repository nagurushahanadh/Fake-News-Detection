from flask import Flask, render_template, request
from transformers import pipeline
from difflib import SequenceMatcher
import requests
import re

app = Flask(__name__)

# =====================================
# Configuration
# =====================================
GOOGLE_API_KEY = "AIzaSyBVCFoCjw5Z8J7rt_yEctjC9RcgcuBYHZo"   # Put your Google API key here (optional)

# Load Hugging Face model once
classifier = pipeline(
    "text-classification",
    model="mrm8488/bert-tiny-finetuned-fake-news-detection"
)


# =====================================
# AI Fake News Classification
# =====================================
def classify_news(text):
    text = text[:512]
    result = classifier(text)[0]
    confidence = round(result['score'] * 100, 2)

    if result['label'] == "LABEL_0":
        prediction = "FAKE"
    else:
        prediction = "REAL"

    return prediction, confidence


# =====================================
# Extract Main Claim
# =====================================
def extract_claim(text):
    sentences = re.split(r'[.!?]', text)
    return sentences[0].strip()


# =====================================
# Utility: Text Similarity
# =====================================
def is_similar(a, b, threshold=0.5):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > threshold


# =====================================
# Google Fact Check Verification
# =====================================
def verify_claim_google(claim):
    if not GOOGLE_API_KEY:
        return "Google check disabled", None

    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    params = {
        "query": claim,
        "key": GOOGLE_API_KEY,
        "languageCode": "en"
    }

    try:
        response = requests.get(url, params=params, timeout=5).json()
        claims = response.get("claims")

        if claims:
            api_claim = claims[0]["text"]

            # Check relevance
            if not is_similar(claim, api_claim):
                return "Fact-check found but not relevant", None

            review = claims[0]["claimReview"][0]
            publisher = review["publisher"]["name"]
            rating = review.get("textualRating", "No rating")
            review_url = review["url"]

            rating_lower = rating.lower()

            if "false" in rating_lower:
                verdict = "FAKE"
            elif "true" in rating_lower:
                verdict = "REAL"
            else:
                verdict = None

            status = f"Reviewed by {publisher} — Rating: {rating} ({review_url})"
            return status, verdict

        return "No fact-check found", None

    except requests.exceptions.RequestException:
        return "Google Fact Check service unavailable", None


# =====================================
# Wikipedia Knowledge Verification
# =====================================
def verify_with_wikipedia(claim):
    search_url = "https://en.wikipedia.org/w/api.php"

    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": claim,
        "format": "json"
    }

    try:
        search_response = requests.get(search_url, params=search_params, timeout=5).json()
        results = search_response.get("query", {}).get("search", [])

        if not results:
            return None

        page_title = results[0]["title"]

        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
        summary_response = requests.get(summary_url, timeout=5).json()

        if "extract" in summary_response and len(summary_response["extract"]) > 80:
            return f"REAL (Verified from Wikipedia: {page_title})"

        return None

    except requests.exceptions.RequestException:
        return None


# =====================================
# Main Route
# =====================================
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    confidence = None
    claim = None
    verification = None

    if request.method == "POST":
        news_text = request.form.get("news")

        if news_text and len(news_text) > 20:

            # Step 1: AI Prediction
            ai_result, confidence = classify_news(news_text)

            # Step 2: Extract claim
            claim = extract_claim(news_text)

            # Step 3: Google Fact Check
            verification, google_verdict = verify_claim_google(claim)

            # Step 4: Final decision priority
            if google_verdict:
                result = google_verdict + " (Verified by Fact-Check)"

            else:
                # Step 5: Wikipedia check
                wiki_result = verify_with_wikipedia(claim)

                if wiki_result:
                    result = wiki_result
                    verification = "Knowledge verified using Wikipedia"

                else:
                    # Step 6: Fallback to AI
                    result = ai_result + " (AI Prediction)"

        else:
            verification = "Please enter valid news text (minimum 20 characters)"

    return render_template(
        "index.html",
        result=result,
        confidence=confidence,
        claim=claim,
        verification=verification
    )


# =====================================
# Run Server
# =====================================
if __name__ == "__main__":
    app.run(debug=True)