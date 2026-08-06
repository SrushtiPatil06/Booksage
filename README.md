# 📚 BookSage — Book Recommendation System

BookSage is a content-based book recommendation system built as a capstone project for a Concept Simplified internship. It recommends books based on mood, genre, and books the user already likes, using TF-IDF and Cosine Similarity, with a live Google Books API fallback for titles outside the dataset.

## Features

- **Mood-based recommendations** — thrilling, relaxing, emotional, adventurous, funny
- **Genre-based recommendations** — top-rated books from any genre in the dataset
- **Liked-books recommendations** — enter up to 5 favorite books, get similar reads
- **Combined filtering** — mix mood, genre, and liked books in a single search
- **Live API fallback** — books not in the dataset are looked up in real time via the Google Books API
- **Explainability** — every recommendation includes a short reason for the match
- **Book & author detail pages** — ratings, descriptions, and other books by the same author
- **Session-based login and search history**
- **Sorting** — by best match, rating, popularity, or similarity

## Tech Stack

- **Python**, **pandas**, **numpy** — data handling
- **NLTK** — text preprocessing (stopwords, lemmatization, POS tagging)
- **scikit-learn** — TF-IDF vectorization and Cosine Similarity
- **Streamlit** — web application interface
- **Google Books API** — description enrichment and fallback lookups

## Project Structure



booksage/
├── app.py               # Streamlit UI and page routing
├── recommender.py        # Recommendation engine (TF-IDF, Cosine Similarity)
├── config.py              # API key loading, mood-to-genre mappings
├── text_cleaning.py       # NLTK text preprocessing
├── Main.ipynb             # Data cleaning, EDA, and model development notebook
├── Data/                  # Raw and processed datasets
├── requirements.txt
└── .env                  
```

## Setup

1. Clone this repository
2. Install dependencies:
```
   pip install -r requirements.txt
```
3. Create a `.env` file in the project root with your Google Books API key:
```
   GOOGLE_BOOKS_API_KEY=your_key_here
```
4. Run the app:
``` 
   streamlit run app.py
```

## Data Pipeline

The dataset is sourced from a Kaggle Goodreads books collection. Missing book descriptions (~4% of the dataset) were filled in using the Google Books API. Text was then cleaned using NLTK (stopword removal, lemmatization with POS tagging) before being vectorized with TF-IDF for similarity comparison. The full process, including exploratory data analysis, is documented in `Main.ipynb`.

## Notes

- Login is session-only; a permanent account system with a real database is a planned future upgrade.
- Similarity scores are not shown directly in the UI, as TF-IDF similarity values on natural text are typically low (even for genuinely similar books), which can be misleading to a general audience.

## Author

Built by Srushti as part of a data science internship capstone project.