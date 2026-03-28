"""
Utilities module - NLP, analysis, and preprocessing utilities
"""
from .predictor import predict_news
from .verifier import verify_news
from .explain import explain_news
from .preprocess import clean_text, extract_keywords, highlight_suspicious_words

__all__ = [
    'predict_news',
    'verify_news',
    'explain_news',
    'clean_text',
    'extract_keywords',
    'highlight_suspicious_words'
]
