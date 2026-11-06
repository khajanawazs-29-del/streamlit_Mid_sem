import ast
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------
st.set_page_config(
    page_title="IMDb Movie Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# CUSTOM DESIGN
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: #0b1220;
        color: #f4f7fb;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111b2d 0%, #172238 100%);
        border-right: 1px solid #2c3b55;
    }
    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 1rem;
        max-width: 1600px;
    }
    .hero {
        background: linear-gradient(110deg, #17243a 0%, #263c5b 55%, #101b2d 100%);
        border: 1px solid #344965;
        border-radius: 12px;
        padding: 17px 22px;
        text-align: center;
        margin-bottom: 10px;
    }
    .hero-title {
        color: white;
        font-size: 27px;
        font-weight: 800;
        line-height: 1.2;
    }
    .hero-subtitle {
        color: #d3deed;
        font-size: 14px;
        margin-top: 4px;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1d385d, #1768ad);
        border: 1px solid #315a85;
        border-radius: 10px;
        padding: 10px 14px;
        min-height: 82px;
    }
    div[data-testid="stMetricLabel"] {
        color: #eaf2ff !important;
        font-size: 12px;
    }
    div[data-testid="stMetricValue"] {
        color: white !important;
        font-size: 25px;
    }
    .section-card {
        background: #151f31;
        border: 1px solid #34435b;
        border-radius: 10px;
        padding: 10px 12px 4px 12px;
        margin-bottom: 8px;
    }
    .section-heading {
        font-weight: 750;
        font-size: 15px;
        color: #f5f7fb;
        margin-bottom: 6px;
    }
    .success-strip {
        background: linear-gradient(90deg, #116b50, #174f43);
        border: 1px solid #238665;
        color: #eafff6;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        font-weight: 600;
        margin: 5px 0 10px 0;
    }
    .sidebar-title {
        font-size: 23px;
        font-weight: 900;
        color: #ffd43b;
        margin-bottom: 0;
    }
    .sidebar-subtitle {
        color: #f1f5fa;
        font-size: 14px;
        font-weight: 700;
        line-height: 1.2;
        margin-top: 2px;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #35445d;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #33445e;
    }
    .stTabs [data-baseweb="tab"] {
        background: #17243a;
        border-radius: 7px 7px 0 0;
        padding: 5px 12px;
        color: #e7edf7;
        font-size: 12px;
    }
    .stTabs [aria-selected="true"] {
        background: #176ec2 !important;
        color: white !important;
    }
    div.stButton > button {
        border-radius: 7px;
        font-weight: 650;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# AUTOMATIC CSV LOADING
# Put this Python file and the CSV in the same folder.
# ---------------------------------------------------------
CSV_PATH = Path(__file__).resolve().parent / "C:\\Users\\KHAJANAWAZ\\OneDrive\\Desktop\\Streamlit Midsem\\ToP 250 movies on imdb in 2026 (2).csv"


@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)


if not CSV_PATH.exists():
    # Also support the original filename if the user renames the file.
    alternative = Path(__file__).resolve().parent / "ToP 250 movies on imdb in 2026.csv"
    if alternative.exists():
        CSV_PATH = alternative
    else:
        st.error("CSV file not found. Keep the IMDb CSV in the same folder as this Python file.")
        st.code("ToP 250 movies on imdb in 2026(1).csv")
        st.stop()

try:
    df = load_data(str(CSV_PATH))
except Exception as exc:
    st.error(f"Could not load the CSV file: {exc}")
    st.stop()


# ---------------------------------------------------------
# DATA PREPARATION - COLUMN NAMES MATCH THE PROVIDED CSV
# ---------------------------------------------------------
required_columns = ["primaryTitle", "averageRating", "numVotes", "genres",
                    "countriesOfOrigin", "grossWorldwide"]

missing = [column for column in required_columns if column not in df.columns]
if missing:
    st.error(f"Required columns missing from CSV: {missing}")
    st.stop()


def parse_list(value):
    if pd.isna(value):
        return []
    try:
        result = ast.literal_eval(str(value))
        if isinstance(result, list):
            return [str(item) for item in result]
    except (ValueError, SyntaxError):
        pass
    return [str(value)]


movies = df.copy()
movies["averageRating"] = pd.to_numeric(movies["averageRating"], errors="coerce")
movies["numVotes"] = pd.to_numeric(movies["numVotes"], errors="coerce").fillna(0)
movies["grossWorldwide"] = pd.to_numeric(movies["grossWorldwide"], errors="coerce")
movies["genres_list"] = movies["genres"].apply(parse_list)
movies["countries_list"] = movies["countriesOfOrigin"].apply(parse_list)
movies["primaryTitle"] = movies["primaryTitle"].fillna("Unknown")
movies = movies.dropna(subset=["averageRating"]).copy()

all_genres = sorted({genre for values in movies["genres_list"] for genre in values})
all_countries = sorted({country for values in movies["countries_list"] for country in values})


def money(value):
    if pd.isna(value):
        return "N/A"
    value = float(value)
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"


def format_country(values):
    return ", ".join(values) if values else "Unknown"


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.markdown('<div class="sidebar-title">IMDb</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-subtitle">Movie Analytics<br>Dashboard</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

selected_page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🔎 Movie Explorer", "🎬 Movie Search"],
    index=0,
    label_visibility="visible"
)

st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ Dataset Information", expanded=True):
    st.write("**Top 250 Movies on IMDb (2026)**")
    st.caption(f"Rows: **{df.shape[0]}**")
    st.caption(f"Columns: **{df.shape[1]}**")
    st.caption("This dataset contains movie titles, ratings, genres, votes, countries and worldwide gross.")

st.sidebar.markdown("---")
st.sidebar.caption("**Created by:** Khaja Nawaz")
st.sidebar.caption("**Date:** 06-11-2026")
st.sidebar.caption("**Section:** 2")


# ---------------------------------------------------------
# HEADER - KPI CARDS ARE THE FIRST MAIN CONTENT
# ---------------------------------------------------------
def show_header_and_kpis():
    st.markdown("""
    <div class="hero">
        <div class="hero-title">🎬 IMDb Movie Analytics Dashboard</div>
        <div class="hero-subtitle">Explore. Analyze. Discover.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎬 Total Movies", f"{len(movies):,}")
    c2.metric("⭐ Average IMDb Rating", f"{movies['averageRating'].mean():.1f}")
    c3.metric("🏆 Highest Rating", f"{movies['averageRating'].max():.1f}")
    c4.metric("👥 Total Votes", f"{int(movies['numVotes'].sum()):,}")


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
if selected_page == "🏠 Dashboard":
    show_header_and_kpis()
    st.markdown("---")

    # Tab strip like the reference dashboard
    tab_genre, tab_rating, tab_gross = st.tabs(
        ["📊 Genre Analysis", "🌗 Rating Analysis", "💰 Gross Collection"]
    )

    # Keep all four graphs visible together, as in the reference screenshot.
    genre_counts = (
        movies.explode("genres_list")["genres_list"]
        .replace("", "Unknown")
        .value_counts()
        .rename_axis("Genre")
        .reset_index(name="Count")
    )

    graph1, graph2 = st.columns(2, gap="small")
    with graph1:
        st.markdown('<div class="section-heading">📊 Movies by Genre</div>', unsafe_allow_html=True)
        fig_genre = px.bar(
            genre_counts, x="Genre", y="Count", text="Count",
            color="Genre", template="plotly_white"
        )
        fig_genre.update_layout(
            height=215, margin=dict(l=12, r=8, t=8, b=8),
            showlegend=False, xaxis_title="Genre", yaxis_title="Count",
            font=dict(size=10)
        )
        st.plotly_chart(fig_genre, use_container_width=True, config={"displayModeBar": False})

    with graph2:
        st.markdown('<div class="section-heading">📊 IMDb Rating Distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            movies, x="averageRating", nbins=12,
            template="plotly_white", color_discrete_sequence=["#3488ed"]
        )
        fig_hist.update_layout(
            height=215, margin=dict(l=12, r=8, t=8, b=8),
            xaxis_title="IMDb Rating", yaxis_title="Count",
            font=dict(size=10)
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    graph3, graph4 = st.columns(2, gap="small")
    with graph3:
        st.markdown('<div class="section-heading">⭐ Rating vs Number of Votes</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            movies, x="averageRating", y="numVotes",
            hover_name="primaryTitle", template="plotly_white",
            color_discrete_sequence=["#1685ed"]
        )
        fig_scatter.update_yaxes(type="log")
        fig_scatter.update_layout(
            height=215, margin=dict(l=12, r=8, t=8, b=8),
            xaxis_title="IMDb Rating", yaxis_title="Number of Votes",
            font=dict(size=10)
        )
        st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

    with graph4:
        st.markdown('<div class="section-heading">🏆 Top 10 Movies by Worldwide Gross</div>', unsafe_allow_html=True)
        top_gross = movies.dropna(subset=["grossWorldwide"]).nlargest(10, "grossWorldwide").sort_values("grossWorldwide")
        if not top_gross.empty:
            fig_gross = px.bar(
                top_gross, x="grossWorldwide", y="primaryTitle",
                orientation="h", template="plotly_white",
                color_discrete_sequence=["#ff9418"]
            )
            fig_gross.update_layout(
                height=215, margin=dict(l=12, r=8, t=8, b=8),
                xaxis_title="Worldwide Gross (USD)", yaxis_title="",
                font=dict(size=9)
            )
            st.plotly_chart(fig_gross, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Worldwide gross values are not available.")

    st.markdown(
        '<div class="success-strip">✅ Dashboard loaded successfully! Enjoy exploring the top 250 movies on IMDb.</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # LOWER SECTION: MOVIE EXPLORER + MOVIE SEARCH SIDE BY SIDE
    # -----------------------------------------------------
    left_panel, right_panel = st.columns([1.55, 1], gap="small")

    with left_panel:
        st.markdown('<div class="section-heading">🔎 Interactive Movie Explorer</div>', unsafe_allow_html=True)

        f1, f2, f3 = st.columns([1, 1, 1])
        with f1:
            chosen_genre = st.selectbox("Genre", ["All"] + all_genres, key="dash_genre")
            chosen_countries = st.multiselect("Countries", all_countries, default=[], key="dash_country")
        with f2:
            low_rating = float(movies["averageRating"].min())
            high_rating = float(movies["averageRating"].max())
            rating_filter = st.slider(
                "IMDb Rating", min_value=low_rating, max_value=high_rating,
                value=(low_rating, high_rating), key="dash_rating"
            )
            min_votes = st.number_input("Min Votes", min_value=0, value=0, step=10000, key="dash_votes")
        with f3:
            title_filter = st.text_input("Search Title", placeholder="Enter movie title...", key="dash_title")
            sort_by = st.radio("Sort Order", ["Descending", "Ascending"], key="dash_sort")

        filtered = movies.copy()
        if chosen_genre != "All":
            filtered = filtered[filtered["genres_list"].apply(lambda genres: chosen_genre in genres)]
        if chosen_countries:
            filtered = filtered[
                filtered["countries_list"].apply(lambda countries: any(c in countries for c in chosen_countries))
            ]
        filtered = filtered[filtered["averageRating"].between(rating_filter[0], rating_filter[1])]
        filtered = filtered[filtered["numVotes"] >= min_votes]
        if title_filter.strip():
            filtered = filtered[
                filtered["primaryTitle"].str.contains(title_filter.strip(), case=False, na=False)
            ]
        filtered = filtered.sort_values(
            "averageRating", ascending=(sort_by == "Ascending")
        )

        count_col, reset_col = st.columns([1, 1])
        count_col.info(f"**Filtered Movies: {len(filtered)}**")
        if reset_col.button("↻ Reset Filters", key="dash_reset", use_container_width=True):
            for key in ["dash_genre", "dash_country", "dash_rating", "dash_votes", "dash_title", "dash_sort"]:
                st.session_state.pop(key, None)
            st.rerun()

        display = filtered[[
            "primaryTitle", "genres", "countriesOfOrigin",
            "averageRating", "numVotes", "grossWorldwide"
        ]].copy()
        display.columns = ["Title", "Genre", "Country", "IMDb Rating", "Votes", "Worldwide Gross"]
        display["Worldwide Gross"] = display["Worldwide Gross"].apply(money)
        display["Country"] = display["Country"].apply(lambda value: format_country(parse_list(value)))
        st.dataframe(display.head(100), use_container_width=True, hide_index=True, height=180)

    with right_panel:
        st.markdown('<div class="section-heading">🎬 Movie Search (Form + Session State)</div>', unsafe_allow_html=True)

        if "selected_movie" not in st.session_state:
            st.session_state.selected_movie = None
        if "selected_movie_genre" not in st.session_state:
            st.session_state.selected_movie_genre = None

        with st.form("dashboard_movie_search"):
            search_title = st.text_input("Movie Title", placeholder="e.g. Inception")
            preferred_genre = st.selectbox("Preferred Genre", ["All"] + all_genres, key="search_genre")
            minimum_rating = st.slider(
                "Minimum IMDb Rating", 0.0, 10.0, 7.0, 0.1, key="search_rating"
            )
            search_submit = st.form_submit_button("🔍 Search Movie", use_container_width=True)

        if search_submit:
            results = movies.copy()
            if search_title.strip():
                results = results[
                    results["primaryTitle"].str.contains(search_title.strip(), case=False, na=False)
                ]
            results = results[results["averageRating"] >= minimum_rating]
            if preferred_genre != "All":
                results = results[results["genres_list"].apply(lambda genres: preferred_genre in genres)]

            results = results.sort_values("averageRating", ascending=False)
            if not results.empty:
                st.session_state.selected_movie = results.iloc[0].to_dict()
                st.session_state.selected_movie_genre = preferred_genre
            else:
                st.session_state.selected_movie = None
                st.session_state.selected_movie_genre = None

        if st.session_state.selected_movie is not None:
            selected = st.session_state.selected_movie
            st.markdown(f"**{selected['primaryTitle']}**")
            details1, details2 = st.columns(2)
            details1.caption(f"Genre: {st.session_state.selected_movie_genre or ', '.join(selected['genres_list'])}")
            details1.caption(f"IMDb Rating: {selected['averageRating']:.1f}")
            details2.caption(f"Votes: {int(selected['numVotes']):,}")
            if pd.notna(selected.get("primaryImage")):
                st.image(selected["primaryImage"], width=75)
            st.success("Movie found successfully!")
        elif search_submit:
            st.warning("No matching movie found!")
        else:
            st.caption("Search for a movie to view its details.")


# ---------------------------------------------------------
# STANDALONE MOVIE EXPLORER PAGE
# ---------------------------------------------------------
elif selected_page == "🔎 Movie Explorer":
    st.title("🔎 Interactive Movie Explorer")
    chosen_genre = st.selectbox("Select Genre", ["All"] + all_genres, key="standalone_genre")
    chosen_countries = st.multiselect("Select Countries", all_countries, key="standalone_country")
    rating_bounds = st.slider(
        "IMDb Rating Range",
        float(movies["averageRating"].min()),
        float(movies["averageRating"].max()),
        (float(movies["averageRating"].min()), float(movies["averageRating"].max())),
        key="standalone_rating"
    )
    minimum_votes = st.number_input("Minimum Votes", min_value=0, value=0, key="standalone_votes")
    title_query = st.text_input("Search Movie Title", key="standalone_title")
    order = st.radio("Sort Order", ["Descending", "Ascending"], horizontal=True, key="standalone_sort")

    result = movies.copy()
    if chosen_genre != "All":
        result = result[result["genres_list"].apply(lambda genres: chosen_genre in genres)]
    if chosen_countries:
        result = result[result["countries_list"].apply(lambda countries: any(c in countries for c in chosen_countries))]
    result = result[result["averageRating"].between(*rating_bounds)]
    result = result[result["numVotes"] >= minimum_votes]
    if title_query.strip():
        result = result[result["primaryTitle"].str.contains(title_query.strip(), case=False, na=False)]
    result = result.sort_values("averageRating", ascending=(order == "Ascending"))
    st.metric("Total Filtered Movies", len(result))
    st.dataframe(result[["primaryTitle", "genres", "countriesOfOrigin", "averageRating", "numVotes", "grossWorldwide"]],
                 use_container_width=True, hide_index=True)


# ---------------------------------------------------------
# STANDALONE MOVIE SEARCH PAGE
# ---------------------------------------------------------
elif selected_page == "🎬 Movie Search":
    st.title("🎬 Movie Search (Form + Session State)")
    if "standalone_selected_movie" not in st.session_state:
        st.session_state.standalone_selected_movie = None

    with st.form("standalone_movie_search"):
        title = st.text_input("Enter Movie Title")
        genre = st.selectbox("Preferred Genre", ["All"] + all_genres)
        min_rating = st.slider("Minimum IMDb Rating", 0.0, 10.0, 7.0, 0.1)
        submitted = st.form_submit_button("Search Movie")

    if submitted:
        result = movies.copy()
        if title.strip():
            result = result[result["primaryTitle"].str.contains(title.strip(), case=False, na=False)]
        result = result[result["averageRating"] >= min_rating]
        if genre != "All":
            result = result[result["genres_list"].apply(lambda genres: genre in genres)]
        if result.empty:
            st.session_state.standalone_selected_movie = None
            st.warning("No matching movie found!")
        else:
            st.session_state.standalone_selected_movie = result.sort_values(
                "averageRating", ascending=False
            ).iloc[0].to_dict()

    selected = st.session_state.standalone_selected_movie
    if selected is not None:
        st.subheader("Selected Movie Details")
        st.write("Movie Title:", selected["primaryTitle"])
        st.write("Genre:", ", ".join(selected["genres_list"]))
        st.write("IMDb Rating:", selected["averageRating"])
        st.write("Number of Votes:", f"{int(selected['numVotes']):,}")
        st.success("Movie found successfully!")