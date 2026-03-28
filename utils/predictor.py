from transformers import pipeline
import warnings

warnings.filterwarnings('ignore')

try:
    classifier = pipeline(
        "text-classification",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=0 if False else -1  
    )
    model_loaded = True
except Exception as e:
    print(f"⚠️ Model loading error: {e}")
    model_loaded = False
    classifier = None

def predict_news(text):
    """
    Predict if news is Fake or Real based on sentiment analysis.
    
    Sentiment Model Mapping:
    - NEGATIVE sentiment → FAKE NEWS (likely sensational/misleading)
    - POSITIVE sentiment → REAL NEWS (neutral/factual tone)
    
    Args:
        text (str): News text to analyze
    
    Returns:
        tuple: (label, confidence) where label is 'Fake' or 'Real'
    """
    
    if not model_loaded or classifier is None:
        return "Unable to analyze", 0.0
    
    try:
        text_truncated = text[:512]
        
        results = classifier(text_truncated)
        result = results[0]
        
        label = result['label'].upper()
        score = round(result['score'], 3)
   
        if label == "NEGATIVE":
            return "Fake", score
        else:
            return "Real", score
            
    except Exception as e:
        print(f"❌ Prediction Error: {e}")
        return "Error", 0.0
