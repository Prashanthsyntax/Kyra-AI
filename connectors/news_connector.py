import feedparser
import httpx
from config import NEWS_API_KEY

# Add or remove any RSS feeds you like
RSS_FEEDS = [
    ("NDTV India",  "https://feeds.feedburner.com/ndtvnews-top-stories"),
    ("The Hindu",   "https://www.thehindu.com/news/feeder/default.rss"),
    ("BBC World",   "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Tech Crunch", "https://techcrunch.com/feed/"),
]


def get_rss_headlines(max_per_feed: int = 3) -> str:
    """Fetch top headlines from RSS feeds — no API key needed."""
    lines = []
    for name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            entries = feed.entries[:max_per_feed]
            for e in entries:
                title = e.get("title", "").strip()
                lines.append(f"• [{name}] {title}")
        except Exception:
            pass
    return "\n".join(lines) if lines else "No RSS news fetched."


def get_newsapi_headlines(query: str = "India", page_size: int = 5) -> str:
    """Fetch headlines from NewsAPI.org (100 req/day free)."""
    if not NEWS_API_KEY:
        return get_rss_headlines()
    try:
        url = (
            f"https://newsapi.org/v2/top-headlines"
            f"?country=in&pageSize={page_size}&apiKey={NEWS_API_KEY}"
        )
        resp = httpx.get(url, timeout=10)
        data = resp.json()
        articles = data.get("articles", [])
        lines = [f"• {a['title']}" for a in articles if a.get("title")]
        return "\n".join(lines) if lines else "No news found."
    except Exception as e:
        return f"NewsAPI error: {e}"


def get_top_news() -> str:
    """Primary entry point — tries NewsAPI first, falls back to RSS."""
    if NEWS_API_KEY:
        return get_newsapi_headlines()
    return get_rss_headlines()
