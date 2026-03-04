import os
import json
import datetime
from google import genai
from Bio import Entrez

# --- ARCHITECTURE CONFIGURATION ---
# 最新SDK(google-genai)では、"gemini-1.5-flash" または "gemini-2.0-flash" 
# という短い名称を直接指定するのが現在のベストプラクティスです。
MODEL_ID = "gemini-1.5-flash" 
EMAIL_IDENTITY = "intelligence@liber-med.io"
REVENUE_THRESHOLD = int(os.getenv("TOTAL_REVENUE_LIMIT", 150000))

def get_clinical_insight():
    """世界中の未解決疾患に対する既存薬の転用可能性を抽出する"""
    Entrez.email = EMAIL_IDENTITY
    # 希少疾患や難病に関する最新論文をターゲットにする
    search_query = "(orphan diseases[MeSH Terms]) AND (drug repositioning[Title/Abstract])"
    
    try:
        with Entrez.esearch(db="pubmed", term=search_query, retmax=1, sort='relevance') as handle:
            record = Entrez.read(handle)
        
        if not record["IdList"]:
            return "No critical data found today.", "N/A"
            
        pmid = record["IdList"][0]
        with Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text") as handle:
            abstract = handle.read()
        return abstract, pmid
    except Exception as e:
        return f"Data acquisition failed: {e}", "Error"

def generate_sovereign_report(client, data, pmid):
    """世界の富豪や研究者を惹きつける、最高級の分析レポートを生成"""
    prompt = f"""
    あなたは世界最高峰のバイオテック投資家兼医学博士です。
    以下の論文抄録を読み、以下の4点に絞って『最高級の投資・研究インサイト』をMarkdown形式で執筆してください。

    1. 【Executive Summary】: 1文でこの研究の革命的価値を表現せよ。
    2. 【The Logic of Repositioning】: どの既存薬が、どの難病に、なぜ効くのか。工学的なメカニズムを解説せよ。
    3. 【Market Potential & Social Impact】: この知見が社会に与える影響と、推定される市場価値を論理的に示せ。
    4. 【Ethics & Future Action】: 次に取るべきアクションを1つ提示せよ。

    Abstract Context: {data}
    PMID Reference: {pmid}

    ※出力は専門的かつ、知的な優雅さを感じさせる日本語で行うこと。
    """
    
    # モデル指定の引数を model=MODEL_ID に固定
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

def main():
    # 1. Initialize System
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: raise ValueError("Critical Error: API Key Absent.")
    
    # 2026年最新のクライアント初期化
    client = genai.Client(api_key=api_key)
    
    os.makedirs("reports", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)
    today = datetime.date.today().strftime("%Y-%m-%d")

    # 2. Intelligence Gathering
    abstract, pmid = get_clinical_insight()

    # 3. High-Value Analysis
    report = generate_sovereign_report(client, abstract, pmid)

    # 4. Storage with Immutability
    report_path = f"reports/{today}_insight.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
        f.write(f"\n\n--- \n*This report is part of the Liber-Med Sovereign Wealth Project. Limit: {REVENUE_THRESHOLD} JPY.*")

    # 5. Metadata for Future Scalability
    meta = {"date": today, "pmid": pmid, "status": "completed", "value_score": "high"}
    with open(f"metadata/{today}.json", "w") as f:
        json.dump(meta, f)

    print(f"Sovereign report generated successfully: {report_path}")

if __name__ == "__main__":
    main()
