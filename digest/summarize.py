import os
import re
import time
from google import genai
from google.genai import errors

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODELS = ["gemini-3.8-flash", "gemini-2.5-flash"]  # フォールバック順

PROMPT = """
あなたはAIテクノロジーの専門ジャーナリストです。
以下のAI関連ニュースを、記事ごとに下記のHTML形式で出力してください。
説明文・前置き・コードブロックは不要。HTMLのみ出力してください。
カテゴリタグは記事の category フィールドをそのまま使用してください。

【重要】記事は業界へのインパクト・注目度・話題性が大きい順に並べて出力してください。
カテゴリは関係なく、純粋にニュースとしての重要度でソートすること。

出力形式（記事の数だけ繰り返す）:
<details>
  <summary><strong>{{category}} タイトル（日本語・35字以内）</strong>
  <ul>
    <li>要点1：具体的な数値・事実を含む</li>
    <li>要点2：意義・業界への影響</li>
    <li>要点3：実務・副業・投資への活用ポイント（あれば）</li>
  </ul>
  <p>【詳細】150〜200字で補足。要点で触れなかった背景・経緯・具体例・数値を加え、記事を読まなくても内容が把握できるレベルで書く。</p>
  <p><a href="元URL">📎 詳細を見る（出典：SOURCE）</a></p>
</details>

---
記事リスト:
{articles}
"""

def summarize(articles: list[dict]) -> str:
    text = "\n\n".join(
        f"[{i+1}] category: {a['category']}\ntitle: {a['title']}\n"
        f"URL: {a['url']}\nSource: {a['source']}\n{a['body']}"
        for i, a in enumerate(articles)
    )
    prompt = PROMPT.format(articles=text)

    # モデルごとにリトライ
    for model in MODELS:
        print(f"  モデル試行: {model}")
        for attempt in range(4):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                html = response.text
                html = re.sub(r'<details\s+open[^>]*>', '<details>', html)
                print(f"  ✅ 成功: {model}")
                return html
            except errors.ServerError as e:
                if attempt < 3:
                    wait = 30 * (2 ** attempt)  # 30, 60, 120秒
                    print(f"  ⚠ {model} 503, {wait}秒後にリトライ ({attempt+1}/4)...")
                    time.sleep(wait)
                else:
                    print(f"  ✗ {model} 全リトライ失敗、次のモデルへ")
            except Exception as e:
                print(f"  ✗ {model} エラー: {e}")
                break  # 503以外はすぐ次のモデルへ

    raise RuntimeError("全モデルで生成失敗")
