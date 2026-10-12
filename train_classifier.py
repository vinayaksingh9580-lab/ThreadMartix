import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

def train():
    print("Loading dataset...")
    if not os.path.exists('data/phishing_dataset.csv'):
        print("Dataset not found! Run generate_synthetic_data.py first.")
        return

    df = pd.read_csv('data/phishing_dataset.csv')
    
    # X and y
    X = df['text']
    y = df['label']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Vectorizing text with TF-IDF...")
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("Training Logistic Regression model...")
    # class_weight='balanced' handles imbalanced datasets gracefully
    clf = LogisticRegression(class_weight='balanced', random_state=42)
    clf.fit(X_train_vec, y_train)
    
    print("\n--- Model Evaluation ---")
    y_pred = clf.predict(X_test_vec)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print("\nClassification Report (Precision, Recall, F1):")
    print(classification_report(y_test, y_pred))
    
    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(vectorizer, 'models/vectorizer.joblib')
    joblib.dump(clf, 'models/classifier.joblib')
    print("Saved model and vectorizer to models/ directory.")

if __name__ == '__main__':
    train()
