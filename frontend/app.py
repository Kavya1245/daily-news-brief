import streamlit as st
import requests
from datetime import date, timedelta

import os
API_URL = os.getenv("API_URL", "https://daily-news-brief.onrender.com")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Daily News Brief",
    page_icon="📰",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .brief-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #4f46e5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .article-card {
        background: #f1f5f9;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .category-badge {
        display: inline-block;
        background: #4f46e5;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 13px;
        margin-bottom: 10px;
    }
    .source-tag {
        color: #6b7280;
        font-size: 12px;
    }
    h1 { color: #1e293b; }
    h2 { color: #334155; }
</style>
""", unsafe_allow_html=True)

# ── Helper functions ──────────────────────────────────────────────────────────
CATEGORY_EMOJI = {
    "technology": "💻",
    "business": "💼",
    "sports": "⚽",
    "health": "🏥",
    "entertainment": "🎬",
    "politics": "🏛️",
}

ALL_CATEGORIES = list(CATEGORY_EMOJI.keys())

def get_preferences():
    try:
        r = requests.get(f"{API_URL}/preferences", timeout=5)
        return r.json()
    except:
        return {"categories": ["technology", "business"], "reading_style": "short"}

def save_preferences(categories, reading_style):
    try:
        requests.post(f"{API_URL}/preferences", json={
            "categories": categories,
            "language": "en",
            "reading_style": reading_style
        }, timeout=5)
        return True
    except:
        return False

def fetch_brief(categories, date_str, reading_style):
    try:
        r = requests.post(f"{API_URL}/brief", json={
            "categories": categories,
            "date": date_str,
            "reading_style": reading_style
        }, timeout=120)
        return r.json()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        return None

def render_category_brief(category, data):
    emoji = CATEGORY_EMOJI.get(category, "📌")
    articles = data.get("articles", [])
    brief = data.get("brief", "")
    summaries = data.get("summaries", [])

    with st.expander(f"{emoji} {category.capitalize()} — {len(articles)} articles", expanded=True):
        # Consolidated brief
        st.markdown("#### 📋 Today's Brief")
        st.markdown(f"""<div class='brief-card'>{brief}</div>""", unsafe_allow_html=True)

        # Individual articles
        if articles:
            st.markdown("#### 📄 Articles")
            for i, article in enumerate(articles):
                summary = summaries[i] if i < len(summaries) else article.get("description", "")
                if not summary or summary.strip().lower() in ["none", "null", ""]:
                    summary = article.get("description", "No description available.")
                source = article.get("source", "Unknown")
                url = article.get("url", "")
                title = article.get("title", "No title")

                st.markdown(f"""
                <div class='article-card'>
                    <b>{title}</b><br>
                    <span class='source-tag'>📡 {source}</span><br><br>
                    {summary}
                </div>
                """, unsafe_allow_html=True)

                if url:
                    st.markdown(f"[Read full article →]({url})")
                st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/news.png", width=60)
    st.title("⚙️ Preferences")
    st.markdown("---")

    # Load saved preferences
    saved_prefs = get_preferences()

    selected_categories = st.multiselect(
        "📂 Select Categories",
        options=ALL_CATEGORIES,
        default=saved_prefs.get("categories", ["technology", "business"]),
        format_func=lambda x: f"{CATEGORY_EMOJI.get(x, '📌')} {x.capitalize()}"
    )

    reading_style = st.radio(
        "📖 Reading Style",
        options=["short", "detailed"],
        index=0 if saved_prefs.get("reading_style", "short") == "short" else 1,
        format_func=lambda x: "⚡ Short & Snappy" if x == "short" else "📚 Detailed"
    )

    selected_date = st.date_input(
        "📅 Date",
        value=date.today(),
        min_value=date.today() - timedelta(days=29),
        max_value=date.today()
    )

    st.markdown("---")

    if st.button("💾 Save Preferences", use_container_width=True):
        if save_preferences(selected_categories, reading_style):
            st.success("Preferences saved!")
        else:
            st.error("Could not save preferences.")

    st.markdown("---")

    # ── Past Briefs History Browser ───────────────────────────────────────────
    st.markdown("### 📅 Past Briefs")
    try:
        hist_response = requests.get(f"{API_URL}/history", timeout=5)
        history = hist_response.json().get("history", {})
        if history:
            past_dates = sorted(history.keys(), reverse=True)
            selected_past = st.selectbox(
                "Load a past brief:",
                options=["-- Select a date --"] + past_dates
            )
            if selected_past != "-- Select a date --":
                if st.button("📂 Load This Brief", use_container_width=True):
                    st.session_state["load_past"] = selected_past
        else:
            st.caption("No past briefs yet. Generate one first!")
    except:
        st.caption("History unavailable.")

    st.markdown("---")
    generate_btn = st.button("🚀 Generate My Brief", use_container_width=True, type="primary")

# ── Main page ─────────────────────────────────────────────────────────────────
st.title("📰 Daily News Brief")
st.markdown(f"**{selected_date.strftime('%A, %B %d, %Y')}** · Personalized for you")
st.markdown("---")

# ── Load past brief if selected from history ──────────────────────────────────
if "load_past" in st.session_state and st.session_state["load_past"]:
    past_date = st.session_state["load_past"]
    with st.spinner(f"Loading brief for {past_date}..."):
        try:
            r = requests.get(f"{API_URL}/history/{past_date}", timeout=10)
            past_data = r.json()
            if "error" not in past_data:
                st.info(f"📂 Showing saved brief for **{past_date}**")
                for category, cat_data in past_data.get("categories", {}).items():
                    render_category_brief(category, cat_data)
                st.session_state["load_past"] = None
                st.stop()
            else:
                st.error(f"No saved brief found for {past_date}")
        except Exception as e:
            st.error(f"Could not load past brief: {e}")
    st.session_state["load_past"] = None

# ── Generate new brief ────────────────────────────────────────────────────────
if not selected_categories:
    st.warning("Please select at least one category from the sidebar.")

elif generate_btn:
    with st.spinner("Fetching news and generating your brief... ⏳ (may take 20-30 seconds)"):
        data = fetch_brief(
            categories=selected_categories,
            date_str=str(selected_date),
            reading_style=reading_style
        )

    if data:
        st.success(f"✅ Brief generated for {selected_date.strftime('%B %d, %Y')} — saved to history!")
        categories_data = data.get("categories", {})

        for category in selected_categories:
            if category in categories_data:
                render_category_brief(category, categories_data[category])
            else:
                st.warning(f"No data returned for {category}")

else:
    # ── Welcome screen ────────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; padding: 60px 20px;'>
        <h2>👋 Welcome to your Daily News Brief</h2>
        <p style='font-size:18px; color:#6b7280;'>
            Select your categories and date from the sidebar,<br>
            then click <b>🚀 Generate My Brief</b> to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("💻 Technology\n\nLatest in AI, gadgets, startups")
    with col2:
        st.info("💼 Business\n\nMarkets, economy, companies")
    with col3:
        st.info("🏥 Health\n\nMedical breakthroughs, wellness")
