import os
import json
import datetime
from google import genai
from Bio import Entrez

# --- ARCHITECTURE CONFIGURATION ---
# 2026年現在の最適な安定版を直接指定します
MODEL_ID = "gemini-1.5-flash" 
EMAIL_IDENTITY = "intelligence@liber-med.io"
REVENUE_THRESHOLD = int(os.getenv("TOTAL_REVENUE_LIMIT", 150000))

def get_clinical_insight():
    """世界中の未解決疾患に対する既存薬の転用可能性を抽出する"""
    Entrez.email = EMAIL_IDENTITY
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
    """最高級の分析レポートを生成"""
    prompt = f"""
    あなたは世界最高峰のバイオテック投資家兼医学博士です。
    以下の論文抄録を読み、Markdown形式で分析してください。
    1. 【Executive Summary】 2. 【The Logic of Repositioning】 
    3. 【Market Potential】 4. 【Future Action】

    Context: {data}
    PMID: {pmid}
    """
    
    # 修正ポイント: 複数のモデル名を試行するフェイルセーフ構造
    tried_models = [MODEL_ID, "gemini-2.0-flash", "gemini-1.5-flash-002"]
    
    for model_name in tried_models:
        try:
            print(f"Attempting with model: {model_name}...")
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
            
    raise Exception("All attempted models failed. Please check Google AI Studio project status.")

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: raise ValueError("Critical Error: API Key Absent.")
    
    # クライアント初期化
    client = genai.Client(api_key=api_key)
    
    os.makedirs("reports", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)
    today = datetime.date.today().strftime("%Y-%m-%d")

    # データ取得
    abstract, pmid = get_clinical_insight()

    # AI解析（フェイルセーフ実行）
    report = generate_sovereign_report(client, abstract, pmid)

    # 保存
    report_path = f"reports/{today}_insight.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
        f.write(f"\n\n--- \n*Sovereign Wealth Project. Limit: {REVENUE_THRESHOLD} JPY.*")

    with open(f"metadata/{today}.json", "w") as f:
        json.dump({"date": today, "pmid": pmid, "status": "completed"}, f)

    print(f"Success: {report_path}")

if __name__ == "__main__":
    main()
