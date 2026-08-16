import pandas as pd
import numpy as np
import re
import requests
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import vstack

from config import api_key, API_AVAILABLE, mood_map
from text_cleaning import preprocess_text

# ---------- Load data ----------

df = pd.read_csv("Data/books_preprocessed.csv")
df['cleaned_description'] = df['cleaned_description'].fillna('')

# ---------- Build TF-IDF + Cosine Similarity ----------

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df['cleaned_description'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# ---------- Fetch description for unknown books ----------

LAST_API_ERROR = None

def fetch_description(title, author):
    global LAST_API_ERROR
    LAST_API_ERROR = None

    if not API_AVAILABLE:
        LAST_API_ERROR = "No API key configured."
        return None

    query = f"{title} {author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}"
    try:
        response = requests.get(url, timeout=5)
        st.write("DEBUG - status code:", response.status_code)
        st.write("DEBUG - raw response:", response.text[:500])
        data = response.json()
        if 'items' in data:
            for item in data['items']:
                volume_info = item.get('volumeInfo', {})
                description = volume_info.get('description')
                if description:
                    return description
        return None
    except requests.exceptions.RequestException:
        LAST_API_ERROR = "Could not reach Google Books API. Check your internet connection."
        return None

# ---------- Combined recommendation function ----------

def get_combined_recommendations(mood=None, genre=None, liked_titles=None, num_recommendations=5, sort_by="Best Match"):
    """
    Combines mood, genre, and liked books into a single scoring system
    to produce one blended set of recommendations.
    """
    candidates = df.copy()
    candidates['score'] = 0.0
    candidates['reasons'] = [[] for _ in range(len(candidates))]

    if mood and mood in mood_map:
        genres = mood_map[mood]["genres"]
        pattern = '|'.join(re.escape(g) for g in genres)
        mood_mask = candidates['genre'].str.contains(pattern, case=False, na=False)
        candidates.loc[mood_mask, 'score'] += 1.0
        candidates.loc[mood_mask, 'reasons'] = candidates.loc[mood_mask, 'reasons'].apply(
            lambda r: r + [f"matches your '{mood}' mood"]
        )

    if genre:
        genre_mask = candidates['genre'].str.lower() == genre.lower()
        candidates.loc[genre_mask, 'score'] += 1.0
        candidates.loc[genre_mask, 'reasons'] = candidates.loc[genre_mask, 'reasons'].apply(
            lambda r: r + [f"is in the {genre} genre you selected"]
        )

    liked_indices = []
    liked_vectors_list = []

    if liked_titles:
        seen = set()
        deduped_titles = []
        for t in liked_titles:
            key = t.strip().lower()
            if key and key not in seen:
                seen.add(key)
                deduped_titles.append(t)
        liked_titles = deduped_titles

        for title in liked_titles:
            matches = df[df['title'].str.lower() == title.lower()]
            if not matches.empty:
                idx = matches.index[0]
                liked_indices.append(idx)
                liked_vectors_list.append(tfidf_matrix[idx])
            else:
                description = fetch_description(title, "")
                st.write("DEBUG - description fetched:", description)
                st.write("DEBUG - LAST_API_ERROR:", LAST_API_ERROR)
                if description:
                    cleaned = preprocess_text(description)
                    new_vector = tfidf.transform([cleaned])
                    liked_vectors_list.append(new_vector)

        if liked_vectors_list:
            combined_liked = vstack(liked_vectors_list)
            avg_vector = np.asarray(combined_liked.mean(axis=0))

            sim_scores = cosine_similarity(avg_vector, tfidf_matrix)[0]
            candidates['similarity'] = sim_scores
            candidates['score'] += sim_scores
            top_sim_mask = sim_scores > 0.05
            candidates.loc[top_sim_mask, 'reasons'] = candidates.loc[top_sim_mask, 'reasons'].apply(
                lambda r: r + ["similar in content to books you liked"]
            )
        else:
            candidates['similarity'] = 0.0
    else:
        candidates['similarity'] = 0.0

    candidates = candidates.drop(index=liked_indices, errors='ignore')
    candidates = candidates[candidates['cover_url'].notna()]
    candidates = candidates[candidates['score'] > 0]

    if candidates.empty:
        return None

    pool_size = max(num_recommendations * 4, 20)
    candidates = candidates.sort_values(by=['score', 'average_rating'], ascending=False).head(pool_size)

    if sort_by == "Rating":
        candidates = candidates.sort_values(by='average_rating', ascending=False)
    elif sort_by == "Popularity":
        candidates = candidates.sort_values(by='ratings_count', ascending=False)
    elif sort_by == "Similarity":
        candidates = candidates.sort_values(by='similarity', ascending=False)

    top = candidates.head(num_recommendations).copy()

    top['explanation'] = top['reasons'].apply(
        lambda r: "Recommended because it " + " and ".join(r) + "." if r else "Recommended based on overall match."
    )

    return top[['title', 'authors', 'genre', 'average_rating', 'ratings_count', 'cover_url', 'score', 'similarity', 'explanation']]

# ---------- Author lookup ----------

def get_books_by_author(author_name, exclude_title=None, num_results=5):
    """
    Returns other books by the same author.
    """
    author_books = df[df['authors'].str.contains(re.escape(author_name), case=False, na=False)]
    if exclude_title:
        author_books = author_books[author_books['title'].str.lower() != exclude_title.lower()]
    return author_books[['title', 'genre', 'average_rating', 'cover_url']].head(num_results)