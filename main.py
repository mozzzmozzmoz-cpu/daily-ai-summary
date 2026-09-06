from digest.fetch import fetch_recent
from digest.summarize import summarize
from digest.render import save_html

if __name__ == "__main__":
    print("ニュース取得中...")
    articles = fetch_recent()
    print(f"取得: {len(articles)} 件")

    if not articles:
        print("記事が取得できませんでした。終了します。")
        exit(1)

    print("Gemini で要約中...")
    body = summarize(articles)

    save_html(body, articles)  # ← articles を追加（画像URL受け渡し用）
    print("✅ docs/index.html 生成完了")
