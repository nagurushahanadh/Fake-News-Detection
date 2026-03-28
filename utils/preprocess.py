import re
import string

def clean_text(text):
    """
    Clean and normalize text for analysis.
    
    Args:
        text (str): Raw text input
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
   
    text = re.sub(r'http\S+|www\.\S+', '', text)
  
    text = re.sub(r'\S+@\S+', '', text)
 
    text = re.sub(r'<[^>]+>', '', text)

    text = re.sub(r'\s+', ' ', text)
  
    text = text.lower().strip()
    
    return text

def extract_keywords(text, max_keywords=10):
    """
    Extract important keywords from text.
    
    Args:
        text (str): Text to extract keywords from
        max_keywords (int): Maximum keywords to extract
    
    Returns:
        list: List of keywords
    """
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'can', 'could', 'that', 'this', 'these', 'those'
    }

    text_clean = text.lower()
    text_clean = re.sub(f'[{re.escape(string.punctuation)}]', '', text_clean)
    
    words = text_clean.split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
 
    return list(dict.fromkeys(keywords))[:max_keywords]

def highlight_suspicious_words(text):
    """
    Identify and return suspicious words in text.
    
    Args:
        text (str): Text to analyze
    
    Returns:
        list: List of suspicious words found
    """
    suspicious = [
        "shocking", "breaking", "fake", "alert", "unbelievable",
        "disgusting", "miracle", "cure", "guaranteed", "secret"
    ]
    
    text_lower = text.lower()
    found_words = []
    
    for word in suspicious:
        if word in text_lower:
            found_words.append(word)
    
    return list(dict.fromkeys(found_words))
