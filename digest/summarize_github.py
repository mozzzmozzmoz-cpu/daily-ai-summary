import os
import time
from google import genai
from google.genai import errors

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODELS = ["gemini-3.8-flash"]

PROMPT = """
あなたはGitHubトレンドを解説するエンジニア向けジャーナリストです。
以下のGitHub週間スターランキングTOP10を日本語で解説してください。
説明文・前置き・コードブロックは不要。HTMLのみ出力してください。

出力形式（リポジトリの数だけ繰り返す）:
<details>
  <summary><strong>#{{rank}} {{name}} — 一言タイトル（日本語・30字以内）</strong>
  <ul>
    <li>何ができるか：具体的な機能・用途</li>
    <li>なぜ注目：技術的特徴・ユニークな点</li>
    <li>活用ポイント：エンジニア・副業・自動化への応用</li>
  </ul>
  <p>【詳細】100〜150字で補足。</p>
  <p><a href="URL">⭐ GitHubで見る（総スター: {{total_stars}} / 今週: {{weekly_stars}}）</a></p>
</details>

---
リポジトリ一覧:
{repos}
"""


def summarize_github(repos: list[dict]) -> str:
    text = "\n\n".join(
        f"#{r['rank']} {r['name']}\n"
        f"URL: {r['url']}\n"
        f"言語: {r['language']}\n"
        f"総スター: {r['total_stars']} / 今週: {r['weekly_stars']}\n"
        f"説明: {r['description']}"
        for r in repos
    )
    prompt = PROMPT.format(repos=text)

    for model in MODELS:
        print(f"  モデル試行: {model}")
        for attempt in range(10):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                print(f"  ✅ 成功: {model}")
                return response.text
            except errors.ServerError:
                if attempt < 3:
                    wait = 30 * (2 ** attempt)  # 30, 60, 120秒
                    print(f"  ⚠ {model} 503, {wait}秒後にリトライ ({attempt+1}/4)...")
                    time.sleep(wait)
                else:
                    print(f"  ✗ {model} 全リトライ失敗、次のモデルへ")
            except Exception as e:
                print(f"  ✗ {model} エラー: {e}")
                break

    raise RuntimeError("GitHub要約: 全モデルで生成失敗")
