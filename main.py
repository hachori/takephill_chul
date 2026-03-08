import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 설정 ---
st.set_page_config(page_title="잘챙겨 약!", page_icon="💊")

# --- DB 관리 ---
def init_db():
    conn = sqlite3.connect('supplements.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, time TEXT)''')
    conn.commit()
    conn.close()

def add_log(name):
    conn = sqlite3.connect('supplements.db')
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    conn.execute("INSERT INTO logs (name, date, time) VALUES (?, ?, ?)", (name, date_str, time_str))
    conn.commit()
    conn.close()

def get_today_logs():
    conn = sqlite3.connect('supplements.db')
    today = datetime.now().strftime("%Y-%m-%d")
    df = pd.read_sql(f"SELECT name FROM logs WHERE date = '{today}'", conn)
    conn.close()
    return df['name'].tolist()

# --- 화면 구현 ---
init_db()
st.title("💊 잘챙겨 약!")

# 1. 명언 (나중에 DB나 API로 확장 가능)
st.info("💡 건강은 제1의 재산입니다. 오늘 하루도 성실하게!")

# 2. 영양제 리스트 (본인이 드시는 목록으로 수정하세요)
my_supps = ["영양제 A", "영양제 B", "영양제 C", "영양제 D"]
today_taken = get_today_logs()

st.subheader(f"📅 {datetime.now().strftime('%Y년 %m월 %d일')} 현황")

for supp in my_supps:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"### {supp}")
    with col2:
        if supp in today_taken:
            st.success("복용 완료")
        else:
            if st.button("먹기", key=supp):
                add_log(supp)
                st.rerun()

# 3. 간단한 기록 확인
with st.expander("📝 최근 복용 로그 확인"):
    conn = sqlite3.connect('supplements.db')
    st.table(pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 5", conn))
    conn.close()
