import streamlit as st
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="新闻快讯", layout="wide")
st.title("📰 实时新闻展示（新浪）")

# 初始化刷新状态
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

# ✅ 带调试信息的新浪新闻爬虫
def scrape_news():
    print("[爬虫启动] 正在抓取新浪新闻...")

    url = 'https://news.sina.com.cn/roll/'
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        print(f"[调试] response status: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = []
        for item in soup.select('.news-item'):
            a_tag = item.find('a')
            if a_tag and a_tag.get('href'):
                title = a_tag.get_text(strip=True)
                link = a_tag['href']
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[新闻] {title} - {link}")  # 🔍 打印抓取内容
                news_items.append((title, link, timestamp))

        print(f"[调试] 共抓取到 {len(news_items)} 条新闻")

        # 写入数据库
        conn = sqlite3.connect("news.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                title TEXT,
                link TEXT,
                timestamp TEXT
            )
        ''')
        for news in news_items:
            cursor.execute("SELECT 1 FROM news WHERE title = ? AND link = ?", (news[0], news[1]))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO news (title, link, timestamp) VALUES (?, ?, ?)", news)
        conn.commit()
        conn.close()
        print("[数据库] 新闻数据写入完成")

    except Exception as e:
        print(f"[错误] 抓取新闻失败：{e}")

# 👉 刷新按钮触发爬虫（不使用 experimental_rerun）
if st.button("🔁 获取最新新闻"):
    st.session_state.refresh = True

if st.session_state.refresh:
    scrape_news()
    st.success("✅ 新闻已更新")
    st.session_state.refresh = False

# 📦 展示数据库新闻
conn = sqlite3.connect("news.db")
df = pd.read_sql_query("SELECT * FROM news ORDER BY timestamp DESC LIMIT 20", conn)
conn.close()

st.subheader("📰 最新新闻（来自新浪）")
if df.empty:
    st.warning("⚠️ 当前暂无新闻数据，请点击上方按钮尝试重新抓取。")
else:
    st.table(df)

st.caption(f"数据来源：https://news.sina.com.cn/roll/，最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
