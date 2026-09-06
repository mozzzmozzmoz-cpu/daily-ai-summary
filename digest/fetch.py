import feedparser
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

def _gnews(query: str) -> str:
    """Google News RSS — キーワード検索"""
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=en&gl=US&ceid=US:en"

# ── カテゴリ別フィード ──────────────────────────────
FEED_GROUPS = {
    "🔴 3大AI": [
        "https://openai.com/news/rss.xml",
        "https://www.anthropic.com/rss.xml",
        "https://blog.google/technology/ai/rss/",
        _gnews("OpenAI ChatGPT Claude Gemini new update"),
    ],
    "🎨 画像・動画生成": [
        _gnews("AI image generation Midjourney Stable Diffusion Flux DALL-E"),
        _gnews("AI video generation Sora Runway Kling Veo Pika Hailuo"),
    ],
    "💼 実務・副業・トレンド": [
        _gnews("AI productivity workflow automation tool business 2026"),
        _gnews("AI side hustle freelance earn money passive income"),
        _gnews("AI trend viral new tool launched"),
        "https://www.kdnuggets.com/feed",
        "https://towardsdatascience.com/feed",
    ],
    "📰 一般AIニュース": [
        "https://techcrunch.com/tag/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.wired.com/feed/tag/ai/latest/rss",
        "https://huggingface.co/blog/feed.xml",
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
        "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "https://www.artificialintelligence-news.com/feed/",
        "https://www.technologyreview.com/feed/",
    ],
}

def fetch_recent(max_per_group: int = 3) -> list[dict]:
    articles = []
    seen_urls = set()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=30)

    for group, feeds in FEED_GROUPS.items():
        group_hits = []

        for url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:4]:
                    link = entry.get("link", "")
                    if not link or link in seen_urls:
                        continue
                    parsed = entry.get("published_parsed")
                    if parsed:
                        dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                        if dt < cutoff:
                            continue
                    seen_urls.add(link)
                    group_hits.append({
                        "title":    entry.get("title", ""),
                        "url":      link,
                        "source":   feed.feed.get("title", url),
                        "body":     entry.get("summary", "")[:500],
                        "category": group,
                    })
            except Exception as e:
                print(f"  ⚠ Feed error ({url}): {e}")

        # カテゴリごとに最大 max_per_group 件を確保
        taken = group_hits[:max_per_group]
        articles.extend(taken)
        print(f"{group}: {len(taken)} 件")

    return articles[:15]
