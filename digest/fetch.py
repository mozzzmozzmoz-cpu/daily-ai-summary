import feedparser
import json
import os
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

def _gnews(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=en&gl=US&ceid=US:en"

FEED_GROUPS = {
    "🔴 3大AI": [
        "https://openai.com/news/rss.xml",
        "https://www.anthropic.com/rss.xml",
        "https://blog.google/technology/ai/rss/",
        _gnews("OpenAI ChatGPT Claude Gemini new update"),
        "https://huggingface.co/blog/feed.xml",
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
    "🇯🇵 日本のAI": [
        _gnews("日本 AI 人工知能 新サービス 2026"),
        _gnews("日本 生成AI LLM 企業 導入"),
        _gnews("日本 AI スタートアップ 資金調達"),
        "https://japan.googleblog.com/feeds/posts/default",
        _gnews("site:ascii.jp OR site:itmedia.co.jp OR site:mynavi.jp AI 生成AI"),
    ],
    "🧠 LLM・モデル技術": [
        _gnews("LLM large language model new release benchmark 2026"),
        _gnews("open source LLM Llama Mistral Qwen released"),
        _gnews("AI model fine-tuning RLHF reasoning multimodal"),
        "https://huggingface.co/blog/feed.xml",
        _gnews("transformer architecture attention mechanism research"),
    ],
    "📰 一般AIニュース": [
        "https://techcrunch.com/tag/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.wired.com/feed/tag/ai/latest/rss",
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "https://www.artificialintelligence-news.com/feed/",
        "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
        "https://www.technologyreview.com/feed/",
    ],
}

SEEN_CACHE = "docs/seen_urls.json"

def load_seen_urls() -> set:
    if os.path.exists(SEEN_CACHE):
        with open(SEEN_CACHE) as f:
            return set(json.load(f))
    return set()

def save_seen_urls(urls: set):
    url_list = list(urls)[-500:]
    os.makedirs("docs", exist_ok=True)
    with open(SEEN_CACHE, "w") as f:
        json.dump(url_list, f)

def _extract_image(entry) -> str:
    for m in entry.get("media_content", []):
        if m.get("url") and m.get("medium") == "image":
            return m["url"]
    for m in entry.get("media_thumbnail", []):
        if m.get("url"):
            return m["url"]
    for enc in entry.get("enclosures", []):
        if enc.get("type", "").startswith("image/"):
            return enc.get("href", "")
    html = entry.get("summary", "") or (entry.get("content", [{}])[0].get("value", ""))
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    return ""

def fetch_recent(max_per_group: int = 3) -> list[dict]:
    published_seen = load_seen_urls()
    run_seen = set(published_seen)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=30)
    articles = []

    for group, feeds in FEED_GROUPS.items():
        group_hits = []
        for url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:4]:
                    link = entry.get("link", "")
                    if not link or link in run_seen:
                        continue
                    parsed = entry.get("published_parsed")
                    if parsed:
                        dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                        if dt < cutoff:
                            continue
                    run_seen.add(link)
                    group_hits.append({
                        "title":    entry.get("title", ""),
                        "url":      link,
                        "source":   feed.feed.get("title", url),
                        "body":     entry.get("summary", "")[:500],
                        "category": group,
                        "image":    _extract_image(entry),
                    })
            except Exception as e:
                print(f"  ⚠ Feed error ({url}): {e}")
        taken = group_hits[:max_per_group]
        articles.extend(taken)
        print(f"{group}: {len(taken)} 件")

    result = articles[:20]
    save_seen_urls(published_seen | {a["url"] for a in result})
    return result
