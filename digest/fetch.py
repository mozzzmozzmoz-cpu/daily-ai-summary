import feedparser
from datetime import datetime, timezone, timedelta

FEEDS = [
    # ── 大手テックメディア ──
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.wired.com/feed/tag/ai/latest/rss",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
    "https://www.artificialintelligence-news.com/feed/",

    # ── 研究・学術寄り ──
    "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
    "https://www.technologyreview.com/feed/",

    # ── AI企業公式ブログ ──
    "https://openai.com/news/rss.xml",
    "https://www.anthropic.com/rss.xml",
    "https://huggingface.co/blog/feed.xml",
    "https://blog.google/technology/ai/rss/",

    # ── データサイエンス・実務寄り ──
    "https://www.kdnuggets.com/feed",
    "https://towardsdatascience.com/feed",
]

def fetch_recent(max_per_feed: int = 3) -> list[dict]:
    articles = []
    seen_urls = set()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=30)

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                link = entry.get("link", "")
                if link in seen_urls:
                    continue
                # 日付フィルタ（取得できない場合は通す）
                parsed = entry.get("published_parsed")
                if parsed:
                    dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                    if dt < cutoff:
                        continue
                seen_urls.add(link)
                articles.append({
                    "title":  entry.get("title", ""),
                    "url":    link,
                    "source": feed.feed.get("title", url),
                    "body":   entry.get("summary", "")[:500],
                })
        except Exception as e:
            print(f"Feed取得エラー ({url}): {e}")

    return articles[:12]  # 最大12件に増やす
