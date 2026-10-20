import os
import re
from datetime import datetime, timezone


LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#2b7489",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "Ruby": "#701516",
    "Swift": "#ffac45",
    "Kotlin": "#F18E33",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Jupyter Notebook": "#DA5B0B",
}


def _lang_color(lang: str) -> str:
    return LANG_COLORS.get(lang, "#888888")


def _build_cards(repos: list[dict], summary_html: str) -> str:
    # Geminiの<details>ブロックをリポジトリ順に対応付け
    blocks = re.split(r"(?=<details)", summary_html.strip())
    blocks = [b.strip() for b in blocks if b.strip().startswith("<details")]

    cards = ""
    for i, repo in enumerate(repos):
        block = blocks[i] if i < len(blocks) else ""
        lang = repo.get("language", "")
        color = _lang_color(lang)

        cards += f"""
<div class="repo-card">
  <div class="rank">#{repo['rank']}</div>
  <div class="repo-header">
    <a href="{repo['url']}" target="_blank" rel="noopener" class="repo-name">{repo['name']}</a>
    <div class="repo-meta">
      {'<span class="lang"><span class="lang-dot" style="background:' + color + '"></span>' + lang + '</span>' if lang else ''}
      <span class="stars">⭐ {repo['total_stars']}</span>
      {('<span class="weekly">📈 ' + repo['weekly_stars'] + '</span>') if repo.get('weekly_stars') else ''}
    </div>
  </div>
  {'<p class="repo-desc">' + repo['description'] + '</p>' if repo.get('description') else ''}
  <div class="summary-block">{block}</div>
</div>"""
    return cards


def save_github_html(repos: list[dict], summary_html: str):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        dt = datetime.now(timezone.utc)
        display_date = dt.strftime("%-m月%-d日")
    except Exception:
        display_date = today

    cards = _build_cards(repos, summary_html)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitHub Top 10 — {display_date}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=DM+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0a0a0a; --surface: #141414; --border: #2a2a2a;
    --text: #e8e8e8; --muted: #888; --accent: #ff4444;
  }}
  @media (prefers-color-scheme: light) {{
    :root {{ --bg: #f5f5f5; --surface: #fff; --border: #e0e0e0; --text: #111; --muted: #666; }}
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'DM Sans', system-ui, sans-serif; }}
  header {{
    border-bottom: 3px solid var(--accent); padding: 16px 24px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  header h1 {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.7rem; font-weight: 800; letter-spacing: -0.02em;
  }}
  header h1 span {{ color: var(--accent); }}
  .header-right {{ display: flex; align-items: center; gap: 12px; }}
  .date-badge {{
    font-size: 0.75rem; color: var(--muted);
    padding: 4px 10px; border: 1px solid var(--border); border-radius: 4px;
  }}
  .back-link {{ color: var(--muted); font-size: 0.85rem; text-decoration: none; }}
  .back-link:hover {{ color: var(--text); }}
  main {{ max-width: 800px; margin: 0 auto; padding: 24px; }}
  .repo-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px; margin-bottom: 16px;
    transition: border-color 0.15s;
  }}
  .repo-card:hover {{ border-color: var(--accent); }}
  .rank {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.2rem; font-weight: 800; color: var(--accent);
    line-height: 1; margin-bottom: 6px;
  }}
  .repo-name {{
    font-size: 1.1rem; font-weight: 700;
    color: var(--text); text-decoration: none;
  }}
  .repo-name:hover {{ color: var(--accent); }}
  .repo-meta {{
    display: flex; gap: 14px; margin-top: 6px;
    font-size: 0.8rem; color: var(--muted); align-items: center; flex-wrap: wrap;
  }}
  .lang {{ display: flex; align-items: center; gap: 4px; }}
  .lang-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  .stars {{ color: #f1c40f; }}
  .weekly {{ color: #2ecc71; font-weight: 600; }}
  .repo-desc {{ margin: 10px 0 0; font-size: 0.88rem; color: var(--muted); line-height: 1.5; }}
  .summary-block {{ margin-top: 14px; }}
  .summary-block details {{}}
  .summary-block summary {{
    cursor: pointer; font-weight: 600; font-size: 0.9rem;
    list-style: none; padding: 8px 0; display: flex; align-items: flex-start; gap: 6px;
  }}
  .summary-block summary::-webkit-details-marker {{ display: none; }}
  .summary-block summary::before {{ content: "▶"; color: var(--accent); font-size: 0.65rem; margin-top: 3px; flex-shrink: 0; }}
  .summary-block details[open] summary::before {{ content: "▼"; }}
  .summary-block ul {{ margin: 8px 0 8px 20px; font-size: 0.87rem; line-height: 1.75; }}
  .summary-block ul li {{ margin-bottom: 4px; }}
  .summary-block p {{ font-size: 0.87rem; line-height: 1.7; margin-top: 8px; color: var(--muted); }}
  .summary-block a {{ color: var(--accent); text-decoration: none; }}
  .summary-block a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<header>
  <h1>⭐ GitHub <span>Top 10</span></h1>
  <div class="header-right">
    <span class="date-badge">{display_date} 週間</span>
    <a href="../index.html" class="back-link">← Archive</a>
  </div>
</header>
<main>
{cards}
</main>
</body>
</html>"""

    out_dir = os.path.join("docs", "github")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{today}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ GitHub page: {out_path}")
