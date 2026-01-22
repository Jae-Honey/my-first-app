import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="나의 웹 서비스", initial_sidebar_state="collapsed")

# 2. 로그인 세션 관리
if 'login' not in st.session_state:
    st.session_state['login'] = False

# --- 로그인 전 화면 ---
if not st.session_state['login']:
    st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)
    st.title("🔒 Access Required")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("접속"):
        if password == "1234": # 접속 비밀번호
            st.session_state['login'] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")

# --- 로그인 후 메인 화면 ---
else:
    st.title("🔓 환영합니다!")
    
    try:
        # 구글 시트 연결
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 데이터 불러오기
        try:
            df = conn.read(worksheet="sheet1", ttl=0)
        except:
            df = pd.DataFrame(columns=["name", "content", "date", "password"])

        if df is None or df.empty:
            df = pd.DataFrame(columns=["name", "content", "date", "password"])

        st.divider()
        st.subheader("📝 방명록 남기기")

        # 방명록 입력 폼
        with st.form("guestbook_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("닉네임")
            with col2:
                pw = st.text_input("삭제 비밀번호", type="password")
            
            content = st.text_area("메시지")
            submit = st.form_submit_button("남기기")

            if submit:
                if name and content and pw:
                    new_row = pd.DataFrame([{
                        "name": name,
                        "content": content,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "password": str(pw)
                    }])
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(worksheet="sheet1", data=updated_df)
                    st.success("방명록이 저장되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("모든 칸을 채워주세요.")

        st.divider()
        st.subheader("💬 방명록 목록")

        # 최신순 출력 및 삭제 기능
        if not df.empty:
            # 인덱스를 유지한 채 역순으로 정렬
            for i in reversed(range(len(df))):
                row = df.iloc[i]
                with st.container():
                    c1, c2 = st.columns([0.8, 0.2])
                    with c1:
                        st.write(f"**{row['name']}** ({row['date']})")
                        st.info(row['content'])
                    with c2:
                        # 삭제 버튼 영역
                        with st.expander("삭제"):
                            del_pw = st.text_input("비밀번호", type="password", key=f"pw_{i}")
                            if st.button("확인", key=f"btn_{i}"):
                                if str(del_pw) == str(row['password']):
                                    new_df = df.drop(i)
                                    conn.update(worksheet="sheet1", data=new_df)
                                    st.success("삭제 중...")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("불일치")
        else:
            st.write("아직 작성된 글이 없습니다.")

    except Exception as e:
        st.error(f"데이터베이스 연결 오류: {e}")

    # 로그아웃 버튼
    if st.sidebar.button("로그아웃"):
        st.session_state['login'] = False
        st.rerun()
