import os
import json
import datetime
import time
from google import genai
from Bio import Entrez

# --- ARCHITECTURE CONFIGURATION ---
# 2026年現在の最強モデル「Pro」を先頭に、安定の「Flash」を控えに配置
TRIED_MODELS = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"]
EMAIL_IDENTITY = "intelligence@liber-med.io"
REVENUE_THRESHOLD = int(os.getenv("TOTAL_REVENUE_LIMIT", 150000))

def get_clinical_insight():
    """PubMedから世界の難病治療の種を拾う"""
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
    """最高級の分析レポートを生成（多重バックアップ体制）"""
    prompt = f"""
    あなたは世界最高峰のバイオテック投資家兼医学博士です。
    以下の論文抄録を読み、富裕層向けの『最高級の投資・研究インサイト』を執筆してください。

    1. 【Executive Summary】 
    2. 【The Logic of Repositioning】 
    3. 【Market Potential & Social Impact】 
    4. 【Ethics & Future Action】

    Context: {data}
    PMID: {pmid}
    ※知的で優雅な日本語で出力すること。
    """
    
    for model_name in TRIED_MODELS:
        try:
            print(f"Executing with engine: {model_name}...")
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt
            )
            if response.text:
                return response.text
        except Exception as e:
            print(f"Engine {model_name} currently warming up... (Error: {e})")
            time.sleep(2) # サーバーへの負荷を考慮した紳士的な待機
            continue
            
    raise Exception("All engines are currently in maintenance. Please wait for Google's activation.")

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: raise ValueError("Critical Error: API Key Absent.")
    
    client = genai.Client(api_key=api_key)
    
    os.makedirs("reports", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)
    today = datetime.date.today().strftime("%Y-%m-%d")

    abstract, pmid = get_clinical_insight()
    report = generate_sovereign_report(client, abstract, pmid)

    report_path = f"reports/{today}_insight.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
        f.write(f"\n\n--- \n*Sovereign Wealth Management. Annual Limit: {REVENUE_THRESHOLD} JPY.*")

    with open(f"metadata/{today}.json", "w") as f:
        json.dump({"date": today, "pmid": pmid, "status": "active"}, f)

    print(f"Sovereign Intelligence Unit: Report stabilized at {report_path}")

if __name__ == "__main__":
    main()
