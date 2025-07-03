import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

CHROME_DRIVER_PATH = "D:/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

service = Service(executable_path=CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# ✅ 读取 Excel，包括 Name 和 基因 两列
df = pd.read_excel("D:/Desktop/实验1.xlsx")

# ✅ 组合查询关键词："表型+基因"
search_terms = [
    f"{row['Name']} {row['基因']}"
    for _, row in df.iterrows()
    if pd.notna(row['Name']) and pd.notna(row['基因'])
]

results = []

for term in search_terms:
    print(f"🔍 搜索关键词：{term}")
    driver.get(f"https://www.bing.com/search?q={term}")
    time.sleep(2)

    search_items = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo h2 a')[:3]
    for item in search_items:
        title = item.text
        link = item.get_attribute('href')
        results.append({
            '搜索词': term,
            '标题': title,
            '链接': link
        })

driver.quit()

results_df = pd.DataFrame(results)
results_df.to_excel("D:/Desktop/搜索结果_组合查询.xlsx", index=False)
print("✅ 搜索完成，结果保存在：D:/Desktop/搜索结果_组合查询.xlsx")
