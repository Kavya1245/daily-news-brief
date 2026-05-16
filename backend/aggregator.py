import os
import requests
import feedparser
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Map category names to NewsAPI topics and RSS feeds
CATEGORY_CONFIG = {
    "technology": {
        "newsapi_q": "technology OR artificial intelligence OR software",
        "rss": "https://feeds.arstechnica.com/arstechnica/technology-lab"
    },
    "business": {
        "newsapi_q": "business OR economy OR stock market",
        "rss": "https://feeds.bloomberg.com/markets/news.rss"
    },
    "sports": {
        "newsapi_q": "sports OR NBA OR NFL OR cricket",
        "rss": "https://www.espn.com/espn/rss/news"
    },
   "health": {
        "newsapi_q": "health OR medicine OR wellness OR mental health",
        "rss": "https://rss.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC"
    },
    "entertainment": {
        "newsapi_q": "entertainment OR movies OR music",
        "rss": "https://variety.com/feed/"
    },
    "politics": {
        "newsapi_q": "politics OR government OR elections",
        "rss": "https://rss.politico.com/congress.xml"
    },
}

def fetch_from_newsapi(category: str, date: str, max_articles: int = 5) -> list:
    """Fetch articles from NewsAPI for a category and date."""
    if not NEWS_API_KEY:
        return []
    
    config = CATEGORY_CONFIG.get(category, {})
    query = config.get("newsapi_q", category)
    
    # Calculate date range (that day to next day)
    try:
        from_date = datetime.strptime(date, "%Y-%m-%d")
        to_date = from_date + timedelta(days=1)
    except Exception:
        from_date = datetime.today()
        to_date = from_date + timedelta(days=1)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d"),
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": max_articles,
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        articles = []
        for item in data.get("articles", []):
            if item.get("title") and item.get("description"):
                articles.append({
                    "title": item["title"],
                    "description": item.get("description", ""),
                    "source": item.get("source", {}).get("name", "Unknown"),
                    "url": item.get("url", ""),
                    "published_at": item.get("publishedAt", ""),
                })
        return articles
    except Exception as e:
        print(f"NewsAPI error for {category}: {e}")
        return []

def fetch_from_rss(category: str, max_articles: int = 5) -> list:
    """Fetch articles from RSS feed for a category."""
    config = CATEGORY_CONFIG.get(category, {})
    rss_url = config.get("rss")
    if not rss_url:
        return []

    try:
        feed = feedparser.parse(rss_url)
        articles = []
        for entry in feed.entries[:max_articles]:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            if title and summary:
                articles.append({
                    "title": title,
                    "description": summary[:500],  # cap length
                    "source": feed.feed.get("title", "RSS Feed"),
                    "url": entry.get("link", ""),
                    "published_at": entry.get("published", ""),
                })
        return articles
    except Exception as e:
        print(f"RSS error for {category}: {e}")
        return []

def fetch_articles(category: str, date: str) -> list:
    newsapi_articles = fetch_from_newsapi(category, date, max_articles=4)
    rss_articles = fetch_from_rss(category, max_articles=4)

    all_articles = newsapi_articles + rss_articles

    seen_titles = set()
    unique = []
    for a in all_articles:
        title = a.get("title", "").strip()
        description = a.get("description", "") or ""
        description = description.strip()
        if not title or not description or description.lower() in ["none", "null"]:
            continue
        title_key = title.lower()[:60]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique.append(a)

    return unique[:6]