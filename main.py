from digest.fetch import fetch_recent
from digest.summarize import summarize
from digest.render import save_html
from digest.fetch_github import fetch_github_trending
from digest.summarize_github import summarize_github
from digest.render_github import save_github_html
from digest.build_index import build_index

if __name__ == "__main__":
    ai_ok = False
    gh_ok = False

    # ── AI News ──────────────────────────────────────
    print("=== AI ニュース取得中 ===")
    articles = fetch_recent()
    print(f"取得: {len(articles)} 件")
    if articles:
        print("Gemini で要約中...")
        body = summarize(articles)
        save_html(body, articles)
        ai_ok = True
        print("✅ AI Digest 生成完了")
    else:
        print("⚠ AI記事が取得できませんでした")

    # ── GitHub Trending ───────────────────────────────
    print("\n=== GitHub Trending 取得中 ===")
    repos = fetch_github_trending(since="weekly")
    print(f"取得: {len(repos)} 件")
    if repos:
        print("Gemini で要約中...")
        gh_summary = summarize_github(repos)
        save_github_html(repos, gh_summary)
        gh_ok = True
        print("✅ GitHub Top 10 生成完了")
    else:
        print("⚠ GitHub Trending が取得できませんでした")

    # ── index.html 再生成 ─────────────────────────────
    print("\n=== index.html 更新中 ===")
    build_index()

    if not ai_ok and not gh_ok:
        print("❌ 両方とも取得失敗")
        exit(1)
