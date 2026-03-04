import os
import datetime
from Bio import Entrez
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
Entrez.email = "your-email@example.com"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def main():
    os.makedirs("reports", exist_ok=True)
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # 論文検索 & AI解析の簡易フロー
    prompt = "最新の創薬トレンドについて、15万円の収益をNISAに回すためのヒントを1つ出力して。"
    response = model.generate_content(prompt)
    
    with open(f"reports/{today}.md", "w", encoding="utf-8") as f:
        f.write(response.text)
    with open("reports/latest_insight.md", "w", encoding="utf-8") as f:
        f.write(response.text)

if __name__ == "__main__":
    main()
