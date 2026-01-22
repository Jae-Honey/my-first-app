import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import gspread
import time

# 1. 페이지 설정
st.set_page_config(page_title="나의 보안 방명록", layout="centered")

# 2. 로그인 세션 및 연결 설정
if 'login' not in st.session_state:
    st.session_state['login'] = False

conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["connections"]["gsheets"]["spreadsheet"]

# gspread 인증 함수
def get_gspread_client():
    creds_info = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
    }
    return gspread.service_account_from_dict(creds_info)

# --- 로그인 전 화면 ---
if not st.session_state['login']:
    st.title("🔒 관리자 인증")
    password = st.text_input("접속 비밀번호", type="password")
    if st.button("접속"):
        if password == "1234":
            st.session_state['login'] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")

# --- 로그인 후 메인 화면 ---
else:
    # 💡 [필살기] 잔상이 보일 수 있는 모든 UI 요소를 CSS로 강제 제어
    st.markdown("""
        <style>
        /* 데이터프레임이나 테이블 형태의 모든 자동 출력을 숨김 */
        div[data-testid="stDataFrameResizer"], 
        div[data-testid="stTable"],
        pre { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📝 우리들의 방명록")

    # 데이터 로드
    def load_data():
        data = conn.read(worksheet="sheet1", ttl=0)
        if data is not None and not data.empty:
            return data.astype(str).replace(r'\.0$', '', regex=True)
        return pd.DataFrame(columns=["name", "content", "date", "password"])

    df = load_data()

    # --- 방명록 작성 폼 ---
    with st.form("guestbook_form", clear_on_submit=True):
        st.subheader("새 글 남기기")
        name = st.text_input("닉네임")
        pw = st.text_input("삭제 비밀번호", type="password")
        content = st.text_area("메시지")
        submit = st.form_submit_button("방명록 등록")

        if submit:
            if name and content and pw:
                # 💡 등록 시 즉시 화면을 덮는 스피너 가동
                with st.spinner("방명록을 안전하게 배달 중..."):
                    gc = get_gspread_client()
                    sheet = gc.open_by_url(url).worksheet("sheet1")
                    new_row = [name, content, datetime.now().strftime("%Y-%m-%d %H:%M"), str(pw).strip()]
                    sheet.append_row(new_row)
                    st.cache_data.clear()
                    time.sleep(0.5) # 잔상이 사라질 때까지의 아주 짧은 유예 시간
                st.rerun()

    st.divider()

    # --- 목록 출력 및 삭제 ---
    if not df.empty:
        for i in reversed(range(len(df))):
            row = df.iloc[i]
            with st.container():
                c1, c2 = st.columns([0.8, 0.2])
                with c1:
                    st.write(f"**{row['name']}** <small style='color:gray;'>({row['date']})</small>", unsafe_allow_html=True)
                    st.info(row['content'])
                with c2:
                    with st.expander("삭제"):
                        del_pw = st.text_input("비번", type="password", key=f"pw_{i}")
                        if st.button("확인", key=f"btn_{i}"):
                            if str(del_pw).strip() == str(row['password']).split('.')[0].strip():
                                with st.spinner("삭제 기록 보관 중..."):
                                    gc = get_gspread_client()
                                    ss = gc.open_by_url(url)
                                    # 백업 및 삭제
                                    ss.worksheet("deleted_logs").append_row(row.tolist())
                                    ss.worksheet("sheet1").delete_rows(i + 2)
                                    st.cache_data.clear()
                                    time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("비번 불일치")
    
    if st.sidebar.button("로그아웃"):
        st.session_state['login'] = False
        st.rerun()
