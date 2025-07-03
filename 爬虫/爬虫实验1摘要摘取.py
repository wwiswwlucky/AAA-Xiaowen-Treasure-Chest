import requests
from bs4 import BeautifulSoup
import re
import time

headers = {
    "User-Agent": "Mozilla/5.0"
}

def extract_sentences(text, keywords):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if all(k.lower() in s.lower() for k in keywords)]

def get_abstract(pmid):
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    abstract_div = soup.find("div", class_="abstract-content")
    if abstract_div:
        return abstract_div.get_text(separator=" ", strip=True)
    return ""

def search_pubmed_with_abstracts(query, max_results=5):
    url = f"https://pubmed.ncbi.nlm.nih.gov/?term={query.replace(' ', '+')}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    articles = soup.select(".docsum-content")[:max_results]
    results = []

    for art in articles:
        title_tag = art.select_one("a.docsum-title")
        if title_tag:
            title = title_tag.text.strip()
            href = title_tag.get("href", "")
            pmid = href.strip("/").split("/")[-1]
            abstract = get_abstract(pmid)
            keywords = re.findall(r'"([^"]+)"', query)  # 从查询提取关键词
            co_sentences = extract_sentences(abstract, keywords)
            result = {
                "PMID": pmid,
                "标题": title,
                "摘要": abstract,
                "是否共现": "是" if co_sentences else "否",
                "共现句子": co_sentences[0] if co_sentences else ""
            }
            results.append(result)
            time.sleep(1)  # 避免请求过快
    return results

# 示例使用
query = '"Retinal atrophy" AND ABCA4'
results = search_pubmed_with_abstracts(query, max_results=5)

# 打印结果
for r in results:
    print(f"\n📌 PMID: {r['PMID']}")
    print(f"🔹 标题: {r['标题']}")
    print(f"📄 是否共现: {r['是否共现']}")
    print(f"🧠 共现句子: {r['共现句子']}")
    print(f"📑 摘要: {r['摘要']}")
