import os
import re
from datetime import datetime


def build_index():
    docs_dir = "docs"
    github_dir = os.path.join(docs_dir, "github")

    # AI News ページ一覧
    ai_pages = []
    if os.path.isdir(docs_dir):
        for fname in sorted(os.listdir(docs_dir), reverse=True):
            if re.match(r"\d{4}-\d{2}-\d{2}\.html$", fname):
                date_str = fname.replace(".html", "")
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    display = dt.strftime("%-m月%-d日")
                except Exception:
                    display = date_str
                ai_pages.append((date_str, display, fname))

    # GitHub Trending ページ一覧
    gh_pages = []
    if os.path.isdir(github_dir):
        for fname in sorted(os.listdir(github_dir), reverse=True):
            if re.match(r"\d{4}-\d{2}-\d{2}\.html$", fname):
                date_str = fname.replace(".html", "")
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    display = dt.strftime("%-m月%-d日")
                except Exception:
                    display = date_str
                gh_pages.append((date_str, display, f"github/{fname}"))

    def make_links(pages, label):
        if not pages:
            return '<p class="empty">まだ記事がありません</p>'
        return "\n".join(
            f'<a href="{path}" class="archive-link">'
            f'<span class="date">{display}</span>'
            f'<span class="label">{label}</span>'
            f'</a>'
            for _, display, path in pages
        )

    ai_links = make_links(ai_pages, "AI Daily Digest")
    gh_links = make_links(gh_pages, "GitHub Top 10")

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Digest Archive</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=DM+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0a0a0a; --surface: #141414; --border: #2a2a2a;
    --text: #e8e8e8; --muted: #888; --accent: #ff4444;
    --tab-active: #fff;
  }}
  @media (prefers-color-scheme: light) {{
    :root {{
      --bg: #f5f5f5; --surface: #fff; --border: #e0e0e0;
      --text: #111; --muted: #666; --tab-active: #111;
    }}
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'DM Sans', system-ui, sans-serif; min-height: 100vh; }}
  header {{
    border-bottom: 3px solid var(--accent);
    padding: 18px 24px;
    display: flex; align-items: center; gap: 12px;
  }}
  header h1 {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em;
  }}
  header h1 span {{ color: var(--accent); }}
  .tabs {{
    display: flex; gap: 0;
    border-bottom: 1px solid var(--border);
    padding: 0 24px;
    background: var(--surface);
    position: sticky; top: 0; z-index: 10;
  }}
  .tab {{
    padding: 14px 22px; cursor: pointer;
    font-size: 0.9rem; font-weight: 600;
    color: var(--muted);
    border-bottom: 3px solid transparent;
    transition: all 0.15s;
    user-select: none;
  }}
  .tab.active {{ color: var(--tab-active); border-bottom-color: var(--accent); }}
  .tab:hover:not(.active) {{ color: var(--text); }}
  .tab-content {{ display: none; padding: 24px; max-width: 640px; margin: 0 auto; }}
  .tab-content.active {{ display: block; }}
  .archive-link {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 18px; margin-bottom: 10px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; text-decoration: none; color: var(--text);
    transition: border-color 0.15s, transform 0.1s;
  }}
  .archive-link:hover {{ border-color: var(--accent); transform: translateX(3px); }}
  .archive-link .date {{ font-size: 1.05rem; font-weight: 700; }}
  .archive-link .label {{ font-size: 0.78rem; color: var(--muted); }}
  .empty {{ color: var(--muted); padding: 32px; text-align: center; font-size: 0.9rem; }}
</style>
</head>
<body>
<header>
  <h1>AI Digest <span>Archive</span></h1>
</header>
<div class="tabs">
  <div class="tab active" onclick="switchTab('ai')">📰 AI News</div>
  <div class="tab" onclick="switchTab('github')">⭐ Git Top 10</div>
</div>
<div id="tab-ai" class="tab-content active">
{ai_links}
</div>
<div id="tab-github" class="tab-content">
{gh_links}
</div>
<script>
function switchTab(name) {{
  var tabs = document.querySelectorAll('.tab');
  var contents = document.querySelectorAll('.tab-content');
  var names = ['ai', 'github'];
  tabs.forEach(function(t, i) {{ t.classList.toggle('active', names[i] === name); }});
  contents.forEach(function(c) {{ c.classList.remove('active'); }});
  document.getElementById('tab-' + name).classList.add('active');
}}
</script>
</body>
</html>"""

    os.makedirs(docs_dir, exist_ok=True)
    out = os.path.join(docs_dir, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ index.html 更新 (AI:{len(ai_pages)}件 / GitHub:{len(gh_pages)}件)")
