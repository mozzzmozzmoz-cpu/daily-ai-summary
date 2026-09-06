import feedparser
from datetime import datetime, timezone, timedelta

FEEDS = [
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://venturebeat.com/category/ai/feed/",
]

def fetch_recent(max_per_feed: int = 3) -> list[dict]:
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=30)

    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_per_feed]:
            parsed = entry.get("published_parsed")
            if parsed:
                dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                if dt < cutoff:
                    continue
            articles.append({
                "title":  entry.get("title", ""),
                "url":    entry.get("link", ""),
                "source": feed.feed.get("title", url),
                "body":   entry.get("summary", "")[:500],
            })

    return articles[:10]
