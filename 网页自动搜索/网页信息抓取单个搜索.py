import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ✅ ChromeDriver 路径（你已经下载好了）
CHROME_DRIVER_PATH = "D:/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"

# ✅ 设置 Chrome 浏览器选项
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# ✅ 启动 Chrome 浏览器
service = Service(executable_path=CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# ✅ 读取 Excel 中的搜索关键词
df = pd.read_excel("D:/Desktop/实验1.xlsx")  # 确保 'Name' 是列名
search_terms = df['Name'].dropna().tolist()

# ✅ 存储搜索结果
results = []

for term in search_terms:
    print(f"🔍 搜索关键词：{term}")
    driver.get(f"https://www.bing.com/search?q={term}")
    time.sleep(2)

    # 提取前3条搜索结果（标题 + 链接）
    search_items = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo h2 a')[:3]
    for item in search_items:
        title = item.text
        link = item.get_attribute('href')
        results.append({
            '搜索词': term,
            '标题': title,
            '链接': link
        })

# ✅ 关闭浏览器
driver.quit()

# ✅ 保存为 Excel 文件
results_df = pd.DataFrame(results)
#results_df.to_excel("搜索结果整理.xlsx", index=False)
results_df.to_excel("D:/Desktop/搜索结果整理.xlsx", index=False)
print("✅ 搜索完成，结果保存在 搜索结果整理.xlsx")

