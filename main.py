import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import pytz

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

def add_log(name, tz):
    conn = sqlite3.connect('supplements.db')
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    conn.execute("INSERT INTO logs (name, date, time) VALUES (?, ?, ?)", (name, date_str, time_str))
    conn.commit()
    conn.close()

def get_today_logs(tz):
    conn = sqlite3.connect('supplements.db')
    today = datetime.now(tz).strftime("%Y-%m-%d")
    df = pd.read_sql(f"SELECT name FROM logs WHERE date = '{today}'", conn)
    conn.close()
    return df['name'].tolist()

# --- 화면 구현 ---
init_db()

# --- 타임존 설정 (사이드바) ---
st.sidebar.title("⚙️ 접속 위치 설정")
if 'timezone' not in st.session_state:
    st.session_state['timezone'] = 'Asia/Seoul' # 기본값을 한국으로 설정

# 접속 국가/도시에 맞게 타임존을 선택할 수 있도록 제공
selected_tz = st.sidebar.selectbox(
    "🌍 현재 위치 (타임존)", 
    pytz.common_timezones, 
    index=pytz.common_timezones.index(st.session_state['timezone'])
)
st.session_state['timezone'] = selected_tz
local_tz = pytz.timezone(selected_tz)

# 상단 로고 이미지 배치 (가운데 정렬을 위해 컬럼 사용)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        # 로고 파일이 없을 경우 기존 텍스트 타이틀 표시
        st.title("💊 잘챙겨 약!")

st.markdown("<br>", unsafe_allow_html=True) # 약간의 여백 추가

# 1. 명언
st.info("💡 건강은 제1의 재산입니다. 오늘 하루도 성실하게!")

# 2. 영양제 리스트
my_supps = ["베르베린", "코큐10", "오메가3", "프로폴리스"]
today_taken = get_today_logs(local_tz)

st.subheader(f"📅 {datetime.now(local_tz).strftime('%Y년 %m월 %d일')} 현황")

for supp in my_supps:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"### {supp}")
    with col2:
        if supp in today_taken:
            st.success("복용 완료")
        else:
            if st.button("먹기", key=supp):
                add_log(supp, local_tz)
                st.rerun()

# 3. 간단한 기록 확인
with st.expander("📝 최근 복용 로그 확인"):
    conn = sqlite3.connect('supplements.db')
    # 최근 기록이 없을 때를 대비한 예외 처리
    try:
        df_logs = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 5", conn)
        if df_logs.empty:
            st.write("아직 복용 기록이 없습니다.")
        else:
            st.table(df_logs)
    except Exception as e:
        st.write("기록을 불러오는 중 오류가 발생했습니다.")
    finally:
        conn.close()
