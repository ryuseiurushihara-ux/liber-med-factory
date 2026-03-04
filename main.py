import os
import datetime
from Bio import Entrez
import google.generativeai as genai

# --- [設定エリア] 手動を介さないための環境変数読み込み ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
Entrez.email = "liber-med-bot@example.com" # 形式のみでOK

# Geminiの初期化
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # 2026年最新の高速モデル

def fetch_latest_research():
    """PubMedから最新の創薬・薬物再開発に関する論文を1件取得"""
    search_term = 'drug repositioning[Title/Abstract] OR drug repurposing[Title/Abstract]'
    handle = Entrez.esearch(db="pubmed", term=search_term, retmax=1, sort='relevance')
    record = Entrez.read(handle)
    handle.close()
    
    if not record["IdList"]:
        return None, None

    pmid = record["IdList"][0]
    fetch_handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text")
    abstract_text = fetch_handle.read()
    fetch_handle.close()
    return pmid, abstract_text

def analyze_with_ai(abstract):
    """Geminiにインサイトを生成させる"""
    prompt = f"""
    あなたは高度なバイオインフォマティクス・エンジニアです。
    以下の論文抄録を解析し、エンジニアや投資家、研究者が注目すべき「既存薬の転用可能性」や「新たな市場価値」を報告してください。
    
    【条件】
    1. 専門用語を維持しつつ、論理的かつ工芸的な文章で記述すること。
    2. 既存の薬が別のどの疾患に有効そうか、そのメカニズムを推測すること。
    3. 出力はMarkdown形式で、読みやすい見出しを付けること。
    4. 最後に必ず「本情報はAIによる自動解析であり、医学的アドバイスではありません」と記載すること。

    抄録データ:
    {abstract}
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    # フォルダ準備
    os.makedirs("reports", exist_ok=True)
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # 1. データ取得
    pmid, abstract = fetch_latest_research()
    if not pmid:
        print("No new research found.")
        return

    # 2. AI解析
    print(f"Analyzing PMID: {pmid}...")
    insight_report = analyze_with_ai(abstract)

    # 3. ファイル保存（これがGitHubに自動コミットされる）
    filename = f"reports/{today}_PMID_{pmid}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Daily Drug Insight Report - {today}\n\n")
        f.write(f"**Original Paper (PubMed ID):** [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)\n\n")
        f.write(insight_report)

    # 最新版へのリンク更新（README等からリンクするため）
    with open("reports/latest_insight.md", "w", encoding="utf-8") as f:
        f.write(insight_report)

    print(f"Report saved: {filename}")

if __name__ == "__main__":
    main()
