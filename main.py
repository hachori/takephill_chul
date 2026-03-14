import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import pytz
import streamlit.components.v1 as components

# --- 설정 ---
# 레이아웃을 'wide'로 설정하여 가로 모드에서 화면을 더 넓게 쓰도록 합니다.
st.set_page_config(page_title="잘챙겨 약!", page_icon="💊", layout="wide")

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

# --- 전체화면 토글 버튼 (모바일 우측 하단 플로팅 아이콘) ---
# Streamlit components를 사용하여 안전하게 JavaScript를 실행합니다.
fullscreen_js = """
<script>
    // Streamlit 앱의 메인 DOM에 접근
    const doc = window.parent.document;
    
    // 버튼이 중복 생성되는 것을 방지
    if (!doc.getElementById('fs-btn')) {
        const btn = doc.createElement('button');
        btn.id = 'fs-btn';
        btn.innerHTML = '⛶';
        btn.title = '전체화면 전환';
        btn.style.position = 'fixed';
        btn.style.bottom = '20px';
        btn.style.right = '20px';
        btn.style.zIndex = '999999'; // 어떤 요소보다도 항상 위에 보이도록 최대로 설정
        btn.style.width = '55px';
        btn.style.height = '55px';
        btn.style.fontSize = '26px';
        btn.style.borderRadius = '50%';
        btn.style.border = 'none';
        btn.style.backgroundColor = 'rgba(255, 75, 75, 0.9)';
        btn.style.color = 'white';
        btn.style.boxShadow = '0 4px 6px rgba(0,0,0,0.3)';
        btn.style.cursor = 'pointer';
        btn.style.display = 'flex';
        btn.style.alignItems = 'center';
        btn.style.justifyContent = 'center';
        
        btn.onclick = function() {
            const elem = doc.documentElement;
            const fsElement = doc.fullscreenElement || doc.webkitFullscreenElement;
            if (!fsElement) {
                if (elem.requestFullscreen) elem.requestFullscreen();
                else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen(); // Safari/Chrome 모바일 대응
            } else {
                if (doc.exitFullscreen) doc.exitFullscreen();
                else if (doc.webkitExitFullscreen) doc.webkitExitFullscreen();
            }
        };
        doc.body.appendChild(btn);
    }
</script>
"""
components.html(fullscreen_js, height=0, width=0)

# 상단 로고 이미지 배치 (가로 모드에서 짤리지 않도록 중앙 컬럼 비율을 1->2로 확장)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        # 로고 파일이 없을 경우 기존 텍스트 타이틀 표시 (짤림 방지를 위해 줄바꿈 금지 적용)
        st.markdown("<h2 style='text-align: center; white-space: nowrap;'>💊 잘챙겨 약!</h2>", unsafe_allow_html=True)

# 1. 명언 (상단 여백을 최소화하여 한 화면에 들어오도록 함)
st.info("💡 건강은 제1의 재산입니다. 오늘 하루도 성실하게!")

# 2. 영양제 리스트 (가로 모드 최적화: 4개 열로 분할)
my_supps = ["베르베린", "코큐10", "오메가3", "프로폴리스"]
today_taken = get_today_logs(local_tz)

st.markdown(f"**📅 {datetime.now(local_tz).strftime('%Y년 %m월 %d일')} 현황**")

# 약 개수만큼 가로로 컬럼 생성
supp_cols = st.columns(len(my_supps))

for i, supp in enumerate(my_supps):
    with supp_cols[i]:
        # 모바일 환경에서 텍스트가 잘리지 않도록 가운데 정렬 및 크기 조정
        st.markdown(f"<h4 style='text-align: center; margin-bottom: 10px;'>{supp}</h4>", unsafe_allow_html=True)
        
        if supp in today_taken:
            # 복용 완료 시 체크 표시
            st.success("✅ 완료", icon=None)
        else:
            # 먹기 버튼 (터치하기 쉽게 버튼을 컨테이너 너비에 꽉 채움)
            if st.button("💊 먹기", key=supp, use_container_width=True):
                add_log(supp, local_tz)
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 3. 간단한 기록 확인
with st.expander("📝 최근 복용 로그 확인"):
    conn = sqlite3.connect('supplements.db')
    try:
        df_logs = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 5", conn)
        if df_logs.empty:
            st.write("아직 복용 기록이 없습니다.")
        else:
            # 인덱스를 숨겨 모바일 화면에서 표가 더 넓게 보이도록 처리
            st.dataframe(df_logs, hide_index=True, use_container_width=True)
    except Exception as e:
        st.write("기록을 불러오는 중 오류가 발생했습니다.")
    finally:
        conn.close()
