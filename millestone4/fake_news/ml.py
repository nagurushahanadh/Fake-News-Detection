from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import settings

try:
    import shap  # type: ignore
except ImportError:  # pragma: no cover
    shap = None

try:
    from lime.lime_text import LimeTextExplainer  # type: ignore
except ImportError:  # pragma: no cover
    LimeTextExplainer = None


MODEL_FILENAME = "fake_news_model.joblib"
MODEL_PATH = Path(__file__).resolve().parent / MODEL_FILENAME


@dataclass(frozen=True)
class PredictionResult:
    prediction: str
    confidence: float
    explanation: str
    suspicious_phrases: list[str]
    top_features: list[tuple[str, float]]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _extract_domain(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    m = re.search(r"https?://(www\.)?([a-zA-Z0-9\-\.]+)", url)
    if not m:
        return None
    return m.group(2).lower()


def detect_suspicious_phrases(text: str, phrases: Iterable[str]) -> list[str]:
    
    normalized = _normalize_text(text)
    found: list[str] = []
    for phrase in phrases:
        if phrase.lower() in normalized:
            found.append(phrase)
    return found


def _build_training_data() -> Tuple[List[str], List[int]]:
    

    # Fake/misinformation examples (common sensational language and conspiracy themes)
    fake_texts = [
        "Miracle cure eliminates all diseases overnight.",
        "Shocking truth revealed: governments hide the secret cure.",
        "Breaking secret discovery suppressed by big pharma.",
        "You won't believe what this doctor found.",
        "Cure all cancer with this one trick.",
        "New study proves secret vaccine is being hidden.",
        "Experts say this is the end of disease.",
        "This site reveals the shocking truth behind the pandemic.",
        "The government is lying about climate data to control you.",
        "Scientists admit the moon landing was faked.",
        "This miracle oil burns fat while you sleep.",
        "Secret government program will erase your debt.",
    ]

    # Real-world-like news examples (neutral reporting, factual tone)
    real_texts = [
        "The city council approved the new transit budget today.",
        "Scientists published a peer-reviewed article about climate change.",
        "Local school district reports improved test scores.",
        "Economic forecasts show steady growth for the next quarter.",
        "Health officials encourage vaccination during flu season.",
        "Researchers analyze data from the latest census.",
        "A new species of bird was identified in the Amazon rainforest.",
        "The governor announced a new infrastructure plan.",
        "International trade talks concluded with a new agreement.",
        "A university team developed a more efficient battery technology.",
        "Charities launched a fund to support disaster relief efforts.",
        "Local hospital opens a new pediatric wing after fundraising.",
    ]

    texts = fake_texts + real_texts
    labels = [1] * len(fake_texts) + [0] * len(real_texts)
    return texts, labels


def _train_model(force: bool = False) -> Pipeline:
    """Train a simple TF-IDF + LogisticRegression model for demo purposes."""
    if MODEL_PATH.exists() and not force:
        return joblib.load(MODEL_PATH)

    texts, labels = _build_training_data()

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=2500)),
            ("clf", LogisticRegression(max_iter=500)),
        ]
    )
    pipeline.fit(texts, labels)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def _get_or_train_model() -> Pipeline:
    try:
        return _train_model()
    except Exception:
        # fallback in case training fails
        return _train_model(force=True)


def _get_shap_explanation(text: str, model: Pipeline, top_n: int = 5) -> list[tuple[str, float]]:
    """Return top SHAP feature contributions if SHAP is installed."""
    if shap is None:
        return []

    vectorizer: TfidfVectorizer = model.named_steps["tfidf"]
    clf: LogisticRegression = model.named_steps["clf"]

    # Use a small background dataset for SHAP
    texts, _ = _build_training_data()
    background = vectorizer.transform(texts[:20])

    try:
        explainer = shap.LinearExplainer(clf, background, feature_dependence="independent")
        X = vectorizer.transform([text])
        shap_values = explainer.shap_values(X)
        # shap_values for binary classifier: [class0, class1]
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_vals = shap_values[1][0]
        else:
            shap_vals = shap_values[0][0]
    except Exception:
        return []

    feature_names = np.array(vectorizer.get_feature_names_out())
    top_idx = np.argsort(np.abs(shap_vals))[-top_n:][::-1]
    return [(feature_names[i], float(shap_vals[i])) for i in top_idx if shap_vals[i] != 0.0]


def _get_lime_explanation(text: str, model: Pipeline, top_n: int = 5) -> list[tuple[str, float]]:
    """Return top LIME feature contributions if LIME is installed."""
    if LimeTextExplainer is None:
        return []

    vectorizer: TfidfVectorizer = model.named_steps["tfidf"]

    explainer = LimeTextExplainer(class_names=["Real", "Fake"])
    func = lambda x: model.predict_proba(x)
    exp = explainer.explain_instance(text, func, num_features=top_n)

    # Extract feature and weight
    return [(feat, weight) for feat, weight in exp.as_list()]


def _explain_with_coeffs(text: str, model: Pipeline, top_n: int = 5) -> list[tuple[str, float]]:
    """Return top contributing features using model coefficients."""
    vectorizer: TfidfVectorizer = model.named_steps["tfidf"]
    clf: LogisticRegression = model.named_steps["clf"]

    X = vectorizer.transform([text])
    feature_names = np.array(vectorizer.get_feature_names_out())

    # coefficients for the positive class (fake)
    coefs = clf.coef_[0]
    feature_contrib = X.toarray()[0] * coefs

    top_idxs = np.argsort(feature_contrib)[-top_n:][::-1]
    top_features = [(feature_names[i], float(feature_contrib[i])) for i in top_idxs if feature_contrib[i] != 0.0]

    return top_features


def classify_article(
    title: str,
    content: str,
    url: Optional[str] = None,
    trusted_domains: Optional[Iterable[str]] = None,
) -> PredictionResult:
    """Classify the article as Real or Fake, and provide explainable insights."""

    combined = "\n".join([title or "", content or ""])
    suspicious_phrases = detect_suspicious_phrases(combined, settings.SUSPICIOUS_PHRASES)

    model = _get_or_train_model()

    proba = model.predict_proba([combined])[0]
    fake_confidence = float(proba[1])
    real_confidence = float(proba[0])

    prediction = "Fake News" if fake_confidence >= real_confidence else "Real News"
    confidence = max(fake_confidence, real_confidence)

    # Bonus: Reduce fake confidence if the URL is from a trusted source
    domain = _extract_domain(url)
    if domain and trusted_domains:
        trusted = {d.lower() for d in trusted_domains}
        if any(domain.endswith(td) for td in trusted):
            # penalize fake score
            confidence = confidence * 0.75

    explanation_parts: list[str] = []
    explanation_parts.append(
        "This prediction comes from a TF-IDF + Logistic Regression model trained on a small sample dataset. "
        "Accuracy is limited; use the results as a guide rather than a final verdict."
    )

    if suspicious_phrases:
        explanation_parts.append(
            f"Detected suspicious phrases (often found in misinformation): {', '.join(sorted(set(suspicious_phrases)))}."
        )

    if domain and trusted_domains and any(domain.endswith(td) for td in trusted):
        explanation_parts.append(f"The URL domain {domain} matches a trusted source, so the score was reduced.")

    if not suspicious_phrases:
        explanation_parts.append(
            "No explicit suspicious phrases were found; the prediction is based on the learned text signal."
        )

    # Explain top features (prefer SHAP -> LIME -> coefficient heuristic)
    shap_features = _get_shap_explanation(combined, model, top_n=5)
    lime_features = _get_lime_explanation(combined, model, top_n=5)
    coeff_features = _explain_with_coeffs(combined, model, top_n=5)

    if shap_features:
        explanation_parts.append(
            "SHAP indicates the most influential words for the prediction."
        )
        top_features = shap_features
    elif lime_features:
        explanation_parts.append(
            "LIME indicates the most influential words for the prediction."
        )
        top_features = lime_features
    else:
        explanation_parts.append(
            "Feature importance is derived from the model's coefficients."  # fallback
        )
        top_features = coeff_features

    if top_features:
        feature_explanations = ", ".join(
            f"{name} ({weight:.3f})" for name, weight in top_features
        )
        explanation_parts.append(f"Top influential terms: {feature_explanations}.")

    explanation = " ".join(explanation_parts)

    return PredictionResult(
        prediction=prediction,
        confidence=confidence,
        explanation=explanation,
        suspicious_phrases=suspicious_phrases,
        top_features=top_features,
    )
