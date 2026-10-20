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
        _gnews("local AI image generation ComfyUI Stable Diffusion Flux tutorial 2026"),
        _gnews("AI video generation open source Wan CogVideo Kling Mochi local 2026"),
        _gnews("image video AI model released Flux Midjourney new 2026"),
        _gnews("ComfyUI workflow LoRA Stable Diffusion local run howto"),
    ],
    "💼 実務・副業・トレンド": [
        _gnews("AI productivity workflow automation tool business 2026"),
        _gnews("AI side hustle freelance earn money passive income"),
        _gnews("AI trend viral new tool launched"),
        "https://www.kdnuggets.com/feed",
        "https://towardsdatascience.com/feed",
    ],
    "🇯🇵 日本のAI": [
        _gnews("Sakana AI 研究 新モデル 発表"),
        _gnews("SARASHINA さらしな LLM 日本語モデル"),
        _gnews("日本 生成AI LLM スタートアップ 新サービス 2026"),
        _gnews("日本 AI 研究所 モデル公開 2026"),
        _gnews("site:ascii.jp OR site:itmedia.co.jp OR site:mynavi.jp AI 生成AI LLM"),
    ],
    "🧠 LLM・モデル技術": [
        _gnews("new LLM model released 2026 benchmark SOTA"),
        _gnews("open source LLM Llama Qwen Mistral DeepSeek released 2026"),
        _gnews("AI agent reasoning agentic multi-step tool use 2026"),
        _gnews("LLM local inference Ollama GGUF quantization run 2026"),
        "https://huggingface.co/blog/feed.xml",
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
    """7日以内のURLのみ返す（旧形式リストにも対応）"""
    if not os.path.exists(SEEN_CACHE):
        return set()
    with open(SEEN_CACHE) as f:
        data = json.load(f)
    # 旧形式（リスト）との互換性
    if isinstance(data, list):
        return set(data)
    # 新形式: {"url": "YYYY-MM-DD"} — 7日以内のみ残す
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    return {url for url, date in data.items() if date >= cutoff_date}


def save_seen_urls(urls_with_dates: dict):
    """7日以内のURLのみ保存"""
    os.makedirs("docs", exist_ok=True)
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    pruned = {url: date for url, date in urls_with_dates.items() if date >= cutoff_date}
    with open(SEEN_CACHE, "w") as f:
        json.dump(pruned, f)


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
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
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

    # seen_urls を更新（新形式: url -> date）
    if os.path.exists(SEEN_CACHE):
        with open(SEEN_CACHE) as f:
            existing = json.load(f)
        if isinstance(existing, list):
            existing = {url: "2000-01-01" for url in existing}
    else:
        existing = {}
    existing.update({a["url"]: today for a in result})
    save_seen_urls(existing)

    return result
