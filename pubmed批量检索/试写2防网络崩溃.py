import requests
import re
import xml.etree.ElementTree as ET
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ✅ 创建带重试机制的 requests session
def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session


# ✅ 提取共现句子
def extract_sentences(text, keywords):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in sentences if all(k.lower() in s.lower() for k in keywords)]


# ✅ 查询 PubMed 文献
def query_pubmed(term1, term2, max_results=10):
    query = f"({term1}[Title/Abstract]) AND ({term2}[Title/Abstract])"
    api_key = "a0023c3b4b9be8e47f56fa70878630d9a808"
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    session = create_session()

    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "api_key": api_key
    }

    try:
        search_resp = session.get(search_url, params=search_params, timeout=10)
        search_resp.raise_for_status()
        pmid_list = search_resp.json().get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"❌ PubMed 查询失败：{term1} + {term2}，错误：{e}")
        return [{
            "疾病名称": term1,
            "基因": term2,
            "PMID": "无",
            "标题": "PubMed查询失败",
            "是否共现": "否",
            "共现句子": "无"
        }]

    if not pmid_list:
        return [{
            "疾病名称": term1,
            "基因": term2,
            "PMID": "无",
            "标题": "无相关文献",
            "是否共现": "否",
            "共现句子": "无"
        }]

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pmid_list),
        "retmode": "xml",
        "api_key": api_key
    }

    try:
        fetch_resp = session.get(fetch_url, params=fetch_params, timeout=10)
        fetch_resp.raise_for_status()
    except Exception as e:
        print(f"❌ PubMed 摘要获取失败：{term1} + {term2}，错误：{e}")
        return [{
            "疾病名称": term1,
            "基因": term2,
            "PMID": "无",
            "标题": "摘要获取失败",
            "是否共现": "否",
            "共现句子": "无"
        }]

    root = ET.fromstring(fetch_resp.content)
    results = []

    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle", default="无标题")
        abstract = "".join(elem.text or "" for elem in article.findall(".//AbstractText"))
        pmid = article.findtext(".//PMID", default="无PMID")
        matching_sentences = extract_sentences(abstract, [term1, term2])

        if matching_sentences:
            for sent in matching_sentences:
                results.append({
                    "疾病名称": term1,
                    "基因": term2,
                    "PMID": pmid,
                    "标题": title,
                    "是否共现": "是",
                    "共现句子": sent
                })
        else:
            results.append({
                "疾病名称": term1,
                "基因": term2,
                "PMID": pmid,
                "标题": title,
                "是否共现": "否",
                "共现句子": "无共现句"
            })

    return results


# ✅ 批处理主函数
def batch_process_excel(input_path, output_path):
    df = pd.read_excel(input_path)
    all_results = []

    for index, row in df.iterrows():
        term1 = str(row['Name']).strip()
        term2 = str(row['基因']).strip()
        print(f"🔍 查询：{term1} + {term2}")
        results = query_pubmed(term1, term2)
        all_results.extend(results)

    result_df = pd.DataFrame(all_results)
    result_df.to_excel(output_path, index=False)
    print(f"✅ 所有查询结果已保存至：{output_path}")


# ✅ 示例调用路径
input_excel = r"D:\Desktop\实验1.xlsx"
output_excel = r"D:\Desktop\实验1_结果输出1.xlsx"
batch_process_excel(input_excel, output_excel)
