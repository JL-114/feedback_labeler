import requests
import streamlit as st

# ---- Settings ----------------------------------------------------------
BUSINESS = "a dress rental service"
LABELS = [
    "fit & sizing",
    "garment condition",
    "delivery & logistics",
    "style & inventory",
    "pricing",
    "unclear",
]
GUIDE = """Label the customer comment with exactly one of these labels, covering BOTH positive and negative feedback:
- fit & sizing: comments about garment fit, size accuracy, alterations, too big/small, length, stretch (positive or negative).
- garment condition: comments about cleanliness, stains, wear, damages, zippers, tears, or fresh/clean condition (positive or negative).
- delivery & logistics: comments about shipping speed, arrival timing, packaging, return shipping labels, or general service experience (positive or negative).
- style & inventory: comments about dress availability, color match, designer selection, or how it looked (positive or negative).
- pricing: comments about rental rates, unexpected costs, security deposits, discounts, or value for money (positive or negative).
- unclear: completely ambiguous, off-topic, spam, or lacking any relation to the rental service.

If multiple topics are mentioned, pick the main theme.
Respond with ONLY the exact label name in lowercase."""

MODEL = "openai/gpt-oss-20b"
URL = "https://api.groq.com/openai/v1/chat/completions"
# ------------------------------------------------------------------------


def label_comment(text):
    if not text or not text.strip():
        return "unclear"
        
    key = st.secrets.get("GROQ_API_KEY", st.secrets.get("GROQ-API-KEY", ""))
    if not key:
        return "unclear"
    
    prompt = f"You label customer comments for {BUSINESS}.\n{GUIDE}\n\nComment: {text}"
    
    try:
        response = requests.post(
            URL,
            headers={"Authorization": f"Bearer {key}"},
            json={"model": MODEL, "temperature": 0,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        label = answer.strip().lower()
        
        for valid_label in LABELS:
            if valid_label in label:
                return valid_label
        return "unclear"
    except Exception:
        return "unclear"
