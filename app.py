import streamlit as st
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="新闻快讯", layout="wide")
st.title("📰 实时新闻展示（新浪）")

# ✅ 保证数据库和 news 表存在
def init_db():
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            title TEXT,
            link TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # 👈 初始化数据库结构

# ✅ 初始化 session 状态
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

# ✅ 爬虫函数：抓取新浪新闻
import streamlit as st
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="新闻快讯", layout="wide")
st.title("📰 实时新闻展示（新浪）")

# ✅ 保证数据库和 news 表存在
def init_db():
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            title TEXT,
            link TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # 👈 初始化数据库结构

# ✅ 初始化 session 状态
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

# ✅ 爬虫函数：抓取新浪新闻
def scrape_news():
    print("[爬虫启动] 正在抓取新浪新闻...")

    url = 'https://news.sina.com.cn/roll/'
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        print(f"[调试] response status: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        news_items = []
        for item in soup.select('.news-item'):
            a_tag = item.find('a')
            if a_tag and a_tag.get('href'):
                title = a_tag.get_text(strip=True)
                link = a_tag['href']
                print(f"[新闻] {title} - {link}")
                news_items.append((title, link, timestamp))

        print(f"[调试] 共抓取到 {len(news_items)} 条新闻")

        # ✅ 写入数据库（去重）
        conn = sqlite3.connect("news.db")
        cursor = conn.cursor()
        for news in news_items:
            cursor.execute("SELECT 1 FROM news WHERE title = ? AND link = ?", (news[0], news[1]))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO news (title, link, timestamp) VALUES (?, ?, ?)", news)
        conn.commit()
        conn.close()
        print("[数据库] 新闻数据写入完成")

    except Exception as e:
        print(f"[错误] 抓取新闻失败：{e}")

# ✅ 刷新按钮
if st.button("🔁 获取最新新闻"):
    st.session_state.refresh = True

if st.session_state.refresh:
    scrape_news()
    st.success("✅ 新闻已更新")
    st.session_state.refresh = False

# ✅ 读取并展示新闻内容
conn = sqlite3.connect("news.db")
df = pd.read_sql_query("SELECT * FROM news ORDER BY timestamp DESC LIMIT 20", conn)
conn.close()

st.subheader("📰 最新新闻（来自新浪滚动）")
if df.empty:
    st.warning("⚠️ 当前数据库中暂无新闻，请点击上方按钮尝试更新。")
else:
    st.table(df)

st.caption(f"数据来源：https://news.sina.com.cn/roll/，最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ✅ 刷新按钮
if st.button("🔁 获取最新新闻"):
    st.session_state.refresh = True

if st.session_state.refresh:
    scrape_news()
    st.success("✅ 新闻已更新")
    st.session_state.refresh = False

# ✅ 读取并展示新闻内容
conn = sqlite3.connect("news.db")
df = pd.read_sql_query("SELECT * FROM news ORDER BY timestamp DESC LIMIT 20", conn)
conn.close()

st.subheader("📰 最新新闻（来自新浪滚动）")
if df.empty:
    st.warning("⚠️ 当前数据库中暂无新闻，请点击上方按钮尝试更新。")
else:
    st.table(df)

st.caption(f"数据来源：https://news.sina.com.cn/roll/，最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
