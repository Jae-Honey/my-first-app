import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 (로그인 전에는 사이드바 숨김)
st.set_page_config(page_title="나의 웹 서비스", initial_sidebar_state="collapsed")

# 2. 로그인 세션 관리
if 'login' not in st.session_state:
    st.session_state['login'] = False

# --- 로그인 전 화면 ---
if not st.session_state['login']:
    # CSS로 사이드바 완전히 숨기기
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🔒 Access Required")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    
    if st.button("접속"):
        if password == "1234": # 비밀번호를 원하는 대로 수정하세요
            st.session_state['login'] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")

# --- 로그인 후 메인 화면 ---
else:
    st.title("🔓 환영합니다!")
    st.write("왼쪽 사이드바에서 메뉴를 확인하세요.")
    
    # 구글 시트 연결
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        st.divider()
        st.subheader("📝 방명록")

        # 데이터 불러오기 (워크시트 이름 확인 필수: sheet1)
        df = conn.read(worksheet="sheet1", ttl=0)

        # 방명록 입력 폼
        with st.form("guestbook_form", clear_on_submit=True):
            name = st.text_input("닉네임")
            content = st.text_area("메시지")
            submit = st.form_submit_button("남기기")

            if submit:
                if name and content:
                    # 새 데이터 생성
                    new_data = pd.DataFrame([{
                        "name": name,
                        "content": content,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }])
                    # 기존 데이터에 합치기
                    updated_df = pd.concat([df, new_data], ignore_index=True)
                    # 구글 시트 업데이트
                    conn.update(worksheet="sheet1", data=updated_df)
                    st.success("방명록이 저장되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("이름과 내용을 모두 입력해주세요.")

        # 방명록 목록 출력 (최신순)
        if not df.empty:
            for i, row in df.iloc[::-1].iterrows():
                st.write(f"**{row['name']}** ({row['date']})")
                st.info(row['content'])
        
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류가 발생했습니다: {e}")

    # 로그아웃 버튼
    if st.sidebar.button("로그아웃"):
        st.session_state['login'] = False
        st.rerun()
