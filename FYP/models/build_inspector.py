# CODE FOR: 1_train_inspector.ipynb
import pandas as pd
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor

# --- LOGIC TAGGER (Must match app.py!) ---
def smart_condition_tagger(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    # Priority 1: Excellent (Now includes negation)
    if ("total genuine" in text or "bumper to bumper" in text or "sealed" in text or 
        "no touch" in text or "no paint" in text):
        return text + " TAG_EXCELLENT"
    # Priority 2: Minor (1 or 2 pieces)
    minor_pattern = r"\b(1|one|2|two|3|three)(\s+(or|to|-)\s+(2|two|3|three))?\s*(piece|pc|touch)"
    if re.search(minor_pattern, text) or "minor" in text or "touchup" in text:
        return text + " TAG_GOOD"
    # Priority 3: Fair
    if "shower" in text or "repaint" in text or "fresh look" in text:
        return text + " TAG_FAIR"
    return text

# Load & Train
df = pd.read_csv("gold_data_CLEANED.csv")
df['description'] = df['description'].fillna('').apply(smart_condition_tagger)

vectorizer = TfidfVectorizer(stop_words='english', max_features=2500, ngram_range=(1, 2))
X = vectorizer.fit_transform(df['description'])
y = df['inspection_score']

model = RandomForestRegressor(n_estimators=300, random_state=42)
model.fit(X, y)

joblib.dump(model, "inspector_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
print("✅ Step 1 Complete: Inspector Brain Saved.")