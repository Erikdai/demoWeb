import streamlit as st
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="新闻快讯", layout="wide")
st.title("📰 实时新闻展示")

# 爬虫函数：抓取 Hacker News 标题
def scrape_news():
    url = 'https://news.ycombinator.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    for item in soup.select('.athing'):
        title_tag = item.select_one('.titleline a')
        if title_tag:
            title = title_tag.text.strip()
            link = title_tag['href']
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

st.subheader("最新新闻")
st.table(df)
st.caption(f"数据来源：Hacker News。最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
