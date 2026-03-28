import re

SENSATIONAL_WORDS = [
    "shocking", "breaking", "unbelievable", "alert", "amazing",
    "disgusting", "infuriating", "outrageous", "scandal", "exposed",
    "you won't believe", "doctors hate", "this one trick", "baffled",
    "what happens next"
]

FALSE_CLAIM_INDICATORS = [
    "cure", "miracle", "guaranteed", "eliminate", "proven",
    "secret", "discovered"
]

def explain_news(text):
    """
    Analyze text and provide explanations for credibility assessment.
    
    Args:
        text (str): News text to explain
    
    Returns:
        list: List of explanation points
    """
    reasons = []
    text_lower = text.lower()
    word_count = len(text.split())
 
    sensational_found = []
    for word in SENSATIONAL_WORDS:
        if word in text_lower:
            sensational_found.append(word)
    
    if sensational_found:
        reasons.append(f"⚠️ Sensational language detected: {', '.join(set(sensational_found[:3]))}")
  
    if word_count < 15:
        reasons.append(f"⚠️ Very short text ({word_count} words) - low information content")
    elif word_count > 2000:
        reasons.append(f"📝 Long text ({word_count} words) - detailed content")

    exclamation_count = text.count("!")
    question_count = text.count("?")
    total_punctuation = exclamation_count + question_count
    
    if exclamation_count >= 3:
        reasons.append(f"⚠️ Excessive exclamation marks ({exclamation_count}) - emotional language")
    
    if question_count >= 3:
        reasons.append(f"⚠️ Multiple questions ({question_count}) - may indicate skepticism or doubt")
 
    false_claims_found = []
    for indicator in FALSE_CLAIM_INDICATORS:
        if indicator in text_lower:
            false_claims_found.append(indicator)
    
    if false_claims_found:
        reasons.append(f"⚠️ Unverified claims detected: {', '.join(set(false_claims_found[:2]))}")
   
    urls = re.findall(r'http\S+|www\.\S+', text)
    if urls:
        reasons.append(f"🔗 Contains {len(urls)} link(s) - verify source credibility")
   
    caps_words = len([w for w in text.split() if w.isupper() and len(w) > 1])
    if caps_words >= 3:
        reasons.append(f"⚠️ Multiple words in ALL CAPS - aggressive tone")
 
    positive_indicators = [
        "according to", "research shows", "study found", "data indicates",
        "expert says", "report", "investigation"
    ]
    
    positive_found = 0
    for indicator in positive_indicators:
        if indicator in text_lower:
            positive_found += 1
    
    if positive_found >= 2:
        reasons.append("✅ Uses credible source citations")
    
    if not reasons:
        reasons.append("✅ Neutral and informative language - no red flags detected")
    
    return reasons[:6]  
