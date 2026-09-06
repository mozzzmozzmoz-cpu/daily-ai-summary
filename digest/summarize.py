import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

PROMPT = """
あなたはAIテクノロジーの専門ジャーナリストです。
以下のAI関連ニュースを、記事ごとに下記のHTML形式で出力してください。
説明文・前置き・コードブロックは不要。HTMLのみ出力してください。

出力形式（記事の数だけ繰り返す）:
<details>
  <summary><strong>[カテゴリ] タイトル（日本語・30字以内）</strong></summary>
  <ul>
    <li>要点1：具体的な数値・事実を含む</li>
    <li>要点2：意義・業界への影響</li>
    <li>要点3：今後の展望または注意点</li>
  </ul>
  <p><a href="元URL">📎 詳細を見る</a></p>
</details>

---

記事リスト:
{articles}
"""

def summarize(articles: list[dict]) -> str:
    text = "\n\n".join(
        f"[{i+1}] {a['title']}\nURL: {a['url']}\nSource: {a['source']}\n{a['body']}"
        for i, a in enumerate(articles)
    )
    response = model.generate_content(PROMPT.format(articles=text))
    return response.text
