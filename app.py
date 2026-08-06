import streamlit as st
import pandas as pd

from recommender import (
    get_combined_recommendations,
    get_books_by_author,
    mood_map,
    df,
    API_AVAILABLE,
    LAST_API_ERROR
)
import recommender

st.set_page_config(page_title="BookSage", page_icon="📚", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@600;700&family=Nunito+Sans:wght@400;600&display=swap');
html, body, [class*="css"] {
    font-family: 'Nunito Sans', sans-serif;
    color: #D8E0D3;
}

.stApp {
    background-color: #1F2E23;
}

h1, h2, h3 {
    font-family: 'Lora', serif !important;
    color: #D8E0D3 !important;
}

p, span, label, .stMarkdown, .stCaption {
    color: #D8E0D3 !important;
}

.stButton > button {
    background-color: #6B8068;
    color: #F2F5EF;
    border: 1px solid #8FA888;
    border-radius: 6px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #8FA888;
    color: #1F2E23;
}

[data-testid="stTextInput"] input {
    background-color: #2A3D2F !important;
    color: #D8E0D3 !important;
    border: 1px solid #6B8068 !important;
    border-radius: 6px !important;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #2A3D2F !important;
    border: 1px solid #6B8068 !important;
    border-radius: 6px !important;
}

[data-testid="stExpander"] {
    background-color: #2A3D2F;
    border: 1px solid #6B8068;
    border-radius: 8px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #8FA888 !important;
    border-radius: 10px !important;
    background-color: #2A3D2F;
    padding: 0.5rem;
}

[data-testid="stSidebar"] {
    background-color: #16211A;
}

[data-testid="stSidebar"] * {
    color: #D8E0D3 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background-color: #2A3D2F;
    width: 100%;
    border: 1px solid #6B8068;
}
[data-testid="stHeader"] {
    background-color: #1F2E23;
}

[data-testid="stToolbar"] {
    background-color: #1F2E23;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #6B8068;
}
</style>
""", unsafe_allow_html=True)

# ---------- Initialize session state ----------
if "show_history" not in st.session_state:
    st.session_state.show_history = False
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None
if "selected_author" not in st.session_state:
    st.session_state.selected_author = None

# ---------- Sidebar Navigation ----------
def show_sidebar():
    with st.sidebar:
        st.title("📚 BookSage")
        st.caption(f"Signed in as {st.session_state.user_email}")
        st.divider()

        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "main"
            st.session_state.selected_book = None
            st.session_state.selected_author = None
            st.rerun()

        if st.button("🕘 History", use_container_width=True):
            st.session_state.page = "history"
            st.session_state.selected_book = None
            st.session_state.selected_author = None
            st.rerun()

        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = "settings"
            st.session_state.selected_book = None
            st.session_state.selected_author = None
            st.rerun()

        st.divider()

        if st.button("🚪 Log Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ---------- Welcome Page ----------
def show_welcome_page():
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>📚 BookSage</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; font-size: 1.1rem;'>Your personal book recommendation companion</p>",
            unsafe_allow_html=True
        )
        st.write("")
        st.markdown(
            "<p style='text-align: center; color: #A9B8A5;'>"
            "Discover your next favorite read based on your mood, "
            "favorite genres, and books you already love."
            "</p>",
            unsafe_allow_html=True
        )
        st.write("")
        st.write("")
        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            if st.button("Get Started", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()


# ---------- Login Page ----------
def show_login_page():
    st.write("")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>📚 Welcome Back</h2>", unsafe_allow_html=True)
            st.markdown(
                "<p style='text-align: center; color: #A9B8A5;'>Sign in to continue. "
                "This session is temporary and not saved permanently.</p>",
                unsafe_allow_html=True
            )
            st.write("")

            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            st.write("")
            if st.button("Login / Sign Up", use_container_width=True):
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.page = "main"
                    st.rerun()
                else:
                    st.error("Please enter both email and password.")

            if st.button("← Back", use_container_width=True):
                st.session_state.page = "welcome"
                st.rerun()
                
# ---------- Main Page ----------
def show_main_page():
    st.title("📚 BookSage")
    st.write(f"Welcome, {st.session_state.user_email}!")

    st.subheader("Tell us what you're in the mood for")

    col1, col2 = st.columns(2)

    with col1:
        selected_mood = st.selectbox(
            "Select a mood (optional)",
            options=["None"] + list(mood_map.keys())
        )

    with col2:
        all_genres = sorted(df['genre'].dropna().unique().tolist())
        selected_genre = st.selectbox(
            "Select a genre (optional)",
            options=["None"] + all_genres
        )

    st.write("Enter up to 5 books you've liked (optional)")
    liked_books_input = []
    for i in range(5):
        book = st.text_input(f"Book {i+1}", key=f"liked_book_{i}")
        if book:
            liked_books_input.append(book)
    sort_by = st.selectbox(
        "Sort results by",
        options=["Best Match", "Rating", "Popularity", "Similarity"]
    )
    if st.button("Get Recommendations"):
        mood_param = None if selected_mood == "None" else selected_mood
        genre_param = None if selected_genre == "None" else selected_genre
        liked_param = liked_books_input if liked_books_input else None

        
        results = get_combined_recommendations(
            mood=mood_param,
            genre=genre_param,
            liked_titles=liked_param,
            sort_by=sort_by
        )

        if results is None or results.empty:
            st.warning("No recommendations found. Try different options.")
            
            if recommender.LAST_API_ERROR:
                st.error(f"⚠️ {recommender.LAST_API_ERROR}")
            st.session_state.current_results = None
        else:
            st.session_state.search_history.append({
                "mood": mood_param,
                "genre": genre_param,
                "liked_books": liked_param
            })
            st.session_state.current_results = results
            

    # Display results OUTSIDE the button block, so they persist across reruns
    if st.session_state.current_results is not None:
        results = st.session_state.current_results
        st.subheader("Your Recommendations")
        cols = st.columns(len(results))
        for col, (i, row) in zip(cols, results.iterrows()):
            with col:
                with st.container(border=True):
                    if pd.notna(row['cover_url']):
                        st.image(row['cover_url'], use_container_width=True)
                    else:
                        st.write("No cover")
                    st.markdown(f"**{row['title']}**")
                    st.caption(f"{row['authors']}")
                    st.write(f"⭐ {row['average_rating']}")

                    with st.expander("Why?"):
                        st.write(row['explanation'])
                    if st.button("View Details", key=f"details_{row['title']}"):
                        st.session_state.selected_book = row['title']
                        st.rerun()

  
    # ---------- History Page ----------
def show_history_page():
    st.title("🕘 Your Search History")
    st.caption("This history is only kept for your current session.")

    if st.session_state.search_history:
        for h in reversed(st.session_state.search_history):
            parts = []
            if h["mood"]:
                parts.append(f"mood: {h['mood']}")
            if h["genre"]:
                parts.append(f"genre: {h['genre']}")
            if h["liked_books"]:
                parts.append(f"liked books: {', '.join(h['liked_books'])}")
            st.write("🔎 " + " | ".join(parts))
    else:
        st.info("No searches yet this session.")

# ---------- Settings Page ----------
def show_settings_page():
    st.title("⚙️ Settings")

    st.subheader("Account")
    st.write(f"**Signed in as:** {st.session_state.user_email}")
    st.caption("This is a session-only account. A permanent account system is planned for a future version.")

    st.divider()

    if st.button("🚪 Log Out", key="settings_logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ---------- Book Detail Page ----------
def show_book_details():
    title = st.session_state.selected_book
    book = df[df['title'] == title]

    if book.empty:
        st.error("Book not found.")
        if st.button("Back"):
            st.session_state.selected_book = None
            st.rerun()
        return

    book = book.iloc[0]

    if st.button("← Back to Recommendations"):
        st.session_state.selected_book = None
        st.rerun()

    col1, col2 = st.columns([1, 3])
    with col1:
        if pd.notna(book['cover_url']):
            st.image(book['cover_url'], use_container_width=True)
    with col2:
        st.title(book['title'])
        st.write(f"**Genre:** {book['genre']}")
        st.write(f"**Rating:** ⭐ {book['average_rating']} ({int(book['ratings_count'])} ratings)")
        st.write(f"**Description:** {book['description']}")

        if st.button(f"View author: {book['authors']}"):
            st.session_state.selected_author = book['authors']
            st.rerun()
# ---------- Author Detail Page ----------
def show_author_details():
    author = st.session_state.selected_author

    if st.button("← Back"):
        st.session_state.selected_author = None
        st.rerun()

    st.title(f"✍️ {author}")

    books = get_books_by_author(author)

    if books.empty:
        st.write("No other books found for this author.")
        return

    st.subheader(f"Books by {author}")
    cols = st.columns(min(len(books), 5))
    for col, (i, row) in zip(cols, books.iterrows()):
        with col:
            if pd.notna(row['cover_url']):
                st.image(row['cover_url'], use_container_width=True)
            st.markdown(f"**{row['title']}**")
            st.write(f"⭐ {row['average_rating']}") 


# ---------- Router ----------
if st.session_state.logged_in:
    show_sidebar()

if st.session_state.selected_author:
    show_author_details()
elif st.session_state.selected_book:
    show_book_details()
elif st.session_state.page == "welcome":
    show_welcome_page()
elif st.session_state.page == "login":
    show_login_page()
elif st.session_state.page == "main":
    show_main_page()
elif st.session_state.page == "history":
    show_history_page()
elif st.session_state.page == "settings":
    show_settings_page()