import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0"
}


# ✅ 提取共现句
def extract_sentences(text, keywords):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if all(k.lower() in s.lower() for k in keywords)]


# ✅ 抓取摘要 + 判断 PMC 链接
def get_abstract(pmid):
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # 抽取摘要
    abstract_div = soup.find("div", class_="abstract-content")
    abstract = abstract_div.get_text(separator=" ", strip=True) if abstract_div else ""

    # 抽取 PMC 链接
    pmc_link_tag = soup.select_one("a.link-item.pmc")
    pmc_url = ""
    if pmc_link_tag:
        href = pmc_link_tag.get("href", "")
        pmc_url = href if href.startswith("http") else "https://www.ncbi.nlm.nih.gov" + href

    return abstract, pmc_url


# ✅ 获取 PMC 免费全文内容（增强版）
def get_pmc_full_text(pmc_url):
    try:
        res = requests.get(pmc_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # 优先抓结构化的 <div class="tsec sec">
        sections = soup.find_all("div", class_="tsec sec")
        if sections:
            return "\n\n".join(sec.get_text(separator=" ", strip=True) for sec in sections)

        # 否则抓主内容区
        main = soup.find("div", id="main-content") or soup.find("article")
        return main.get_text(separator=" ", strip=True) if main else "未找到正文内容"
    except Exception as e:
        return f"全文抓取失败: {e}"


# ✅ PubMed 搜索并处理每条文献
def search_pubmed_with_fulltext(query, max_results=5):
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

            # 抓摘要和PMC链接
            abstract, pmc_url = get_abstract(pmid)

            # 共现判断
            keywords = re.findall(r'"([^"]+)"', query)
            co_sentences = extract_sentences(abstract, keywords)

            # 获取全文（如有）
            full_text = get_pmc_full_text(pmc_url) if pmc_url else "无免费全文"

            result = {
                "PMID": pmid,
                "标题": title,
                "摘要": abstract,
                "是否共现": "是" if co_sentences else "否",
                "共现句子": co_sentences[0] if co_sentences else "",
                "是否有免费全文": "是" if pmc_url else "否",
                "PMC链接": pmc_url,
                "全文内容预览": full_text[:500] if "未找到" not in full_text else full_text
            }
            results.append(result)
            time.sleep(1)
    return results


# ✅ 示例运行
query = '"Retinal atrophy" AND ABCA4'
results = search_pubmed_with_fulltext(query, max_results=5)

pd.DataFrame(results).to_excel("D:/Desktop/PubMed_增强版全文爬取.xlsx", index=False)



# ✅ 输出结果
for r in results:
    print(f"\n📌 PMID: {r['PMID']}")
    print(f"🔹 标题: {r['标题']}")
    print(f"📄 是否共现: {r['是否共现']}")
    print(f"🧠 共现句子: {r['共现句子']}")
    print(f"📑 摘要: {r['摘要']}")
    print(f"📖 是否有免费全文: {r['是否有免费全文']}")
    print(f"🔗 PMC链接: {r['PMC链接']}")
    print(f"📄 全文内容预览:\n{r['全文内容预览']}\n")
    print("✅ 结果已保存到 Excel")
