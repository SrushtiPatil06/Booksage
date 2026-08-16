import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

api_key = st.secrets.get("GOOGLE_BOOKS_API_KEY", os.getenv("GOOGLE_BOOKS_API_KEY"))

API_AVAILABLE = api_key is not None and api_key.strip() != ""

mood_map = {
    "Thrilling": {"genres": ["Detective and mystery stories", "Thrillers (Fiction)", "Suspense"]},
    "Relaxing": {"genres": ["Cooking", "Nature", "Travel"]},
    "Emotional": {"genres": ["Fiction", "Biography & Autobiography"]},
    "Adventurous": {"genres": ["Adventure stories", "Fantasy fiction", "Science fiction"]},
    "Funny": {"genres": ["Humor", "Comedy"]}
}