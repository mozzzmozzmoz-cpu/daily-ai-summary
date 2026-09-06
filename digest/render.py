from pathlib import Path
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Digest — {date}</title>
  <style>
    body {{
      font-family: 'Noto Sans JP', sans-serif;
      max-width: 720px;
      margin: 0 auto;
      padding: 20px;
      background: #F4F7FF;
      color: #0B1120;
    }}
    details {{
      background: #fff;
      border: 1px solid #D8E0F3;
      border-radius: 8px;
      padding: 14px 16px;
      margin-bottom: 10px;
    }}
    details[open] {{ border-color: #2457D9; }}
    summary {{
      font-weight: 700;
      cursor: pointer;
      font-size: 15px;
      list-style: none;
    }}
    summary::-webkit-details-marker {{ display: none; }}
    ul {{ padding-left: 20px; margin-top: 10px; }}
    li {{ margin-bottom: 6px; line-height: 1.65; font-size: 14px; }}
    a {{ color: #2457D9; }}
    h1 {{ font-size: 22px; margin-bottom: 4px; }}
    .meta {{ color: #667299; font-size: 13px; margin-bottom: 24px; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #070C1A; color: #E2EAFF; }}
      details {{ background: #0F1828; border-color: #1B2B48; }}
      details[open] {{ border-color: #4D84FF; }}
      a {{ color: #4D84FF; }}
    }}
  </style>
</head>
<body>
  <h1>🤖 AI Digest</h1>
  <p class="meta">{date} JST</p>
  {body}
  <p style="font-size:12px;color:#999;margin-top:32px">
    自動生成 by Gemini + GitHub Actions
  </p>
</body>
</html>"""

def save_html(body: str, path: str = "docs/index.html") -> None:
    date = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    Path(path).parent.mkdir(exist_ok=True)
    Path(path).write_text(HTML.format(date=date, body=body), encoding="utf-8")
