import streamlit as st
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="新闻快讯", layout="wide")
st.title("📰 实时新闻展示")

# ✅ 修改：新浪新闻爬虫函数
def scrape_news():
    url = 'https://news.sina.com.cn/roll/'
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    for item in soup.select('.news-item'):
        a_tag = item.find('a')
        if a_tag and a_tag.get('href'):
            title = a_tag.get_text(strip=True)
            link = a_tag['href']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            news_items.append((title, link, timestamp))

    # 存入数据库（去重）
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

# 每次页面加载时执行爬取
scrape_news()

# 展示新闻
conn = sqlite3.connect("news.db")
df = pd.read_sql_query("SELECT * FROM news ORDER BY timestamp DESC LIMIT 20", conn)
conn.close()

st.subheader("最新新闻（来自新浪新闻滚动页面）")
st.table(df)
st.caption(f"数据来源：https://news.sina.com.cn/roll/ 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
