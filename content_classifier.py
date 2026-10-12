import os
import joblib

# Load models globally so they stay in memory during API use
VECTORIZER_PATH = 'models/vectorizer.joblib'
CLASSIFIER_PATH = 'models/classifier.joblib'

vectorizer = None
classifier = None

def load_models():
    global vectorizer, classifier
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(CLASSIFIER_PATH):
        if vectorizer is None:
            vectorizer = joblib.load(VECTORIZER_PATH)
        if classifier is None:
            classifier = joblib.load(CLASSIFIER_PATH)
        return True
    return False

def classify_email(text):
    """
    Classifies the raw text of an email.
    Returns the predicted label and the confidence score (probability).
    """
    if not text:
        return {"label": "unknown", "confidence": 0.0}
        
    if not load_models():
        return {"error": "Models not trained yet. Run train_classifier.py first."}
        
    # Transform
    vec = vectorizer.transform([text])
    
    # Predict
    prob = classifier.predict_proba(vec)[0]
    classes = classifier.classes_
    
    # Find max probability
    max_idx = prob.argmax()
    predicted_label = classes[max_idx]
    confidence = float(prob[max_idx])
    
    return {
        "label": predicted_label,
        "confidence": confidence
    }

def calculate_fraud_score(ml_result, anomaly_flags):
    """
    Calculates the final Fraud Score (0-100) based on:
    1. NLP Content Classification (Phishing / BEC)
    2. Header Anomalies (SPF/DKIM failures, Lookalike domains, etc)
    
    EXPLAINABLE SCORING FORMULA:
    ----------------------------
    Base Score: Starts at 0.
    
    + Content Penalty (Max 50 pts):
        - If ML predicts 'phishing' or 'bec', we take (confidence * 50).
          E.g., 90% confidence of phishing = 45 points.
        - If ML predicts 'legit', penalty is 0.
        
    + Authentication Anomaly Penalty (Max 50 pts):
        - We assign specific point values to anomaly flags identified in Phase 2.
        - E.g., SPF Misalignment = 20 pts, Missing DKIM = 10 pts, Lookalike Domain = 30 pts.
        - Total anomaly points are capped at 50.
        
    Final Fraud Score = Content Penalty + Anomaly Penalty (Capped at 100)
    
    Thresholds for UI (Phase 5):
    - 0-30: Likely Safe
    - 31-70: Suspicious
    - 71-100: Malicious / High Risk
    """
    
    # 1. Content Penalty
    content_penalty = 0.0
    label = ml_result.get('label', 'unknown')
    conf = ml_result.get('confidence', 0.0)
    
    if label in ['phishing', 'bec']:
        content_penalty = conf * 50.0
        
    # 2. Anomaly Penalty
    anomaly_penalty = 0.0
    
    # Define weights for specific flags (these strings match the outputs from Phase 2)
    flag_weights = {
        "From domain does not match authenticated sending domain (SPF misaligned)": 20,
        "Missing DKIM signature entirely": 10,
        "Reply-To differs from From address (Classic BEC pattern)": 30,
        "SPF fails but email claims to be from a known-strict domain (High Phishing Risk)": 40,
        # We use a partial match for dynamic strings like lookalike domains
        "contains numbers (Possible lookalike/typo-squatting)": 30,
        # New Phase 4 Threat Intel Flags
        "Origin IP is a known Tor exit node": 40,
        "Origin IP is from a VPN/Hosting provider (Non-residential)": 20
    }
    
    for flag in anomaly_flags:
        matched = False
        for key, weight in flag_weights.items():
            if key in flag:
                anomaly_penalty += weight
                matched = True
                break
        # If a flag exists but isn't explicitly weighted, give it a default 10 points
        if not matched:
            anomaly_penalty += 10
            
    # Cap anomaly penalty at 50
    anomaly_penalty = min(anomaly_penalty, 50.0)
    
    # Final Score
    fraud_score = min(content_penalty + anomaly_penalty, 100.0)
    
    return {
        "fraud_score": round(fraud_score, 1),
        "content_penalty": round(content_penalty, 1),
        "anomaly_penalty": round(anomaly_penalty, 1),
        "ml_label": label,
        "ml_confidence": round(conf, 3)
    }
