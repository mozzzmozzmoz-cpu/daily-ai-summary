import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PROMPT = """
あなたはAIテクノロジーの専門ジャーナリストです。
以下のAI関連ニュースを、記事ごとに下記のHTML形式で出力してください。
説明文・前置き・コードブロックは不要。HTMLのみ出力してください。
カテゴリタグは記事の category フィールドをそのまま使用してください。

出力形式（記事の数だけ繰り返す）:
<details>
  <summary><strong>{{category}} タイトル（日本語・35字以内）</strong>
  <ul>
    <li>要点1：具体的な数値・事実を含む</li>
    <li>要点2：意義・業界への影響</li>
    <li>要点3：実務・副業・投資への活用ポイント（あれば）</li>
  </ul>
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
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=PROMPT.format(articles=text),
    )
    return response.text
