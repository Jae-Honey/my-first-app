import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import gspread # 💡 내부 처리를 위한 라이브러리

# 1. 페이지 설정
st.set_page_config(page_title="나의 보안 방명록", layout="centered")

# 2. 로그인 세션 관리
if 'login' not in st.session_state:
    st.session_state['login'] = False

# --- 로그인 전 화면 ---
if not st.session_state['login']:
    st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)
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
    st.title("📝 우리들의 방명록")
    
    try:
        # 구글 시트 연결
        conn = st.connection("gsheets", type=GSheetsConnection)
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        # 💡 잔상 방지를 위한 "조용한" 시트 접근 함수
        def get_silent_client():
            # streamlit-gsheets의 내부 인증 정보를 그대로 재사용합니다.
            return conn._instance.client if hasattr(conn._instance, 'client') else conn._instance

        def get_data(sheet_name):
            try:
                data = conn.read(worksheet=sheet_name, ttl=0)
                if data is not None and not data.empty:
                    data = data.astype(str).replace(r'\.0$', '', regex=True)
                    return data
                return pd.DataFrame(columns=["name", "content", "date", "password"])
            except:
                return pd.DataFrame(columns=["name", "content", "date", "password"])

        df = get_data("sheet1")

        # --- 방명록 작성 폼 ---
        with st.form("guestbook_form", clear_on_submit=True):
            st.subheader("새 글 남기기")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("닉네임")
            with col2:
                pw = st.text_input("삭제 비밀번호", type="password")
            
            content = st.text_area("메시지")
            submit = st.form_submit_button("방명록 등록")

            if submit:
                if name and content and pw:
                    with st.spinner("등록 중..."):
                        # 💡 conn.update를 쓰지 않고 gspread 명령어로 조용히 기록
                        client = get_silent_client()
                        ss = client.open_by_url(url)
                        sheet = ss.worksheet("sheet1")
                        
                        new_row = [name, content, datetime.now().strftime("%Y-%m-%d %H:%M"), str(pw).strip()]
                        sheet.append_row(new_row)
                        
                        st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("모든 항목을 입력해주세요.")

        st.divider()
        st.subheader("💬 방명록 목록")
        
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
                                stored_pw = str(row['password']).split('.')[0].strip()
                                if str(del_pw).strip() == stored_pw:
                                    with st.spinner("삭제 중..."):
                                        client = get_silent_client()
                                        ss = client.open_by_url(url)
                                        
                                        # 1. 백업 (deleted_logs 시트)
                                        log_sheet = ss.worksheet("deleted_logs")
                                        log_sheet.append_row(row.tolist())
                                        
                                        # 2. 삭제 (sheet1 시트)
                                        main_sheet = ss.worksheet("sheet1")
                                        main_sheet.delete_rows(i + 2)
                                        
                                        st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("불일치")
        else:
            st.write("첫 번째 방명록을 남겨보세요! ✨")

    except Exception as e:
        st.error(f"오류 발생: {e}")

    if st.sidebar.button("로그아웃"):
        st.session_state['login'] = False
        st.rerun()
