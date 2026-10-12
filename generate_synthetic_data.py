import os
import pandas as pd
import random

def generate_data():
    os.makedirs('data', exist_ok=True)
    
    legit_templates = [
        "Hi team, just checking in on the project status. Can we meet at {time}?",
        "Please find the attached invoice for last month's services.",
        "Your code review has been completed. Check github for comments.",
        "Reminder: company all-hands meeting tomorrow at {time}.",
        "The server deployment finished successfully without errors."
    ]
    
    phishing_templates = [
        "URGENT: Your account has been suspended. Click here to verify your identity.",
        "You have won a $1000 gift card! Claim it immediately before it expires.",
        "Your password expires in 24 hours. Login here to reset it: http://fake-login.com",
        "Security Alert: Unauthorized login attempt. Verify your details now.",
        "Your invoice #{num} is overdue. Please pay immediately to avoid legal action."
    ]
    
    bec_templates = [
        "I am in a meeting. Need you to process a wire transfer to our new vendor today.",
        "Please change my direct deposit to this new account number immediately.",
        "Are you at your desk? I need a quick favor, buy some Apple gift cards.",
        "Keep this confidential, but we are acquiring a company. Send funds to this account.",
        "I need you to urgently pay this invoice today before the bank closes."
    ]
    
    data = []
    
    # Generate 100 legit
    for _ in range(100):
        t = random.choice(legit_templates).replace("{time}", f"{random.randint(1,12)}:00")
        data.append({"text": t, "label": "legit"})
        
    # Generate 50 phishing
    for _ in range(50):
        t = random.choice(phishing_templates).replace("{num}", str(random.randint(100,999)))
        data.append({"text": t, "label": "phishing"})
        
    # Generate 50 bec
    for _ in range(50):
        data.append({"text": random.choice(bec_templates), "label": "bec"})
        
    df = pd.DataFrame(data)
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv('data/phishing_dataset.csv', index=False)
    print("Generated 200 synthetic emails at data/phishing_dataset.csv")

if __name__ == '__main__':
    generate_data()
