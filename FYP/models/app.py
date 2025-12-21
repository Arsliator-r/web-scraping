import streamlit as st
import pandas as pd
import joblib
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="PakWheels AI Valuator", page_icon="🚗", layout="centered")

# --- 1. LOAD BRAINS ---
@st.cache_resource
def load_models():
    try:
        price_model = joblib.load('price_model.pkl')
        inspector_model = joblib.load('inspector_model.pkl')
        vectorizer = joblib.load('tfidf_vectorizer.pkl')
        return price_model, inspector_model, vectorizer
    except Exception as e:
        return None, None, None

price_model, inspector_model, vectorizer = load_models()

# --- 2. THE "WHISPERER" FUNCTION (CRITICAL: MUST MATCH TRAINING) ---
def smart_condition_tagger(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    
    # Priority 1: Excellent Signals
    if "total genuine" in text or "bumper to bumper" in text or "sealed" in text:
        return text + " TAG_EXCELLENT" 
        
    # Priority 2: Minor/Good Signals (The "2 pieces" logic)
    minor_pattern = r"\b(1|one|2|two|3|three)\s*(piece|pc|touch)"
    if re.search(minor_pattern, text) or "minor" in text or "touchup" in text:
        return text + " TAG_GOOD"
        
    # Priority 3: Negative Signals
    if "shower" in text or "repaint" in text or "fresh look" in text or "showered" in text:
        return text + " TAG_FAIR"
        
    return text

# --- HEADER ---
st.title("🚗 AutoScout: AI Used Car Valuator")
st.markdown("### FYP Project: NLP-Powered Price & Condition Estimator")
st.markdown("---")

if price_model is None:
    st.error("🚨 Critical Error: Model files not found!")
    st.stop()

# --- SIDEBAR (INPUTS) ---
st.sidebar.header("Vehicle Specifications")
car_name = st.sidebar.text_input("Car Name", "Honda Civic Oriel 1.8 i-VTEC CVT 2020")
year = st.sidebar.slider("Model Year", 2005, 2024, 2020)
mileage = st.sidebar.number_input("Mileage (km)", 0, 300000, 50000, step=1000)
engine = st.sidebar.number_input("Engine Capacity (cc)", 600, 6000, 1800, step=100)
trans = st.sidebar.selectbox("Transmission", ["Automatic", "Manual"])
fuel = st.sidebar.selectbox("Fuel Type", ["Petrol", "Diesel", "Hybrid"])

# --- MAIN AREA ---
st.subheader("📝 Seller Description Analysis")
user_desc = st.text_area("Ad Description:", height=150, 
                         placeholder="e.g. 2 pieces touched, rest genuine...",
                         value="only 1 or 2 pieces touchup rest genuine")

if st.button("🚀 Analyze & Value Car", type="primary"):
    
    # --- STEP 1: APPLY THE TAGGER (THE FIX) ---
    # We transform the user's simple text into "Tagged Text" so the AI understands
    tagged_desc = smart_condition_tagger(user_desc)
    
    # Show the user what the AI actually "sees" (Optional Debugging)
    with st.expander("Debug: See Internal AI Logic"):
        st.write(f"Raw Input: '{user_desc}'")
        st.write(f"Processed Input: '{tagged_desc}'")
    
    # --- STEP 2: PREDICT SCORE ---
    desc_vector = vectorizer.transform([tagged_desc])
    predicted_score = inspector_model.predict(desc_vector)[0]
    
    # --- STEP 3: PREDICT PRICE ---
    input_data = pd.DataFrame({
        'title_version': [car_name],
        'model_year': [year],
        'mileage': [mileage],
        'engine': [engine],
        'transmission': [trans],
        'fuel': [fuel],
        'inspection_score': [predicted_score] 
    })
    
    predicted_price = price_model.predict(input_data)[0]
    
    # --- DISPLAY RESULTS ---
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Condition")
        st.metric("AI Score", f"{predicted_score:.1f} / 10")
        if predicted_score >= 9.0: st.success("💎 Pristine")
        elif predicted_score >= 8.0: st.success("✅ Good")
        elif predicted_score >= 7.0: st.warning("⚠️ Fair")
        else: st.error("❌ Rough")
            
    with col2:
        st.subheader("Market Valuation")
        st.metric("Estimated Price", f"PKR {int(predicted_price):,}")