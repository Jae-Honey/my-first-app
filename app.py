import streamlit as st

# 1. 페이지 설정 (사이드바 기본 상태 결정)
st.set_page_config(initial_sidebar_state="collapsed")

# 로그인 세션 상태 초기화
if 'login' not in st.session_state:
    st.session_state['login'] = False

# 로그인 전일 때 스타일 (사이드바를 아예 안 보이게 가림)
if not st.session_state['login']:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 로그인 화면 출력
    st.title("🔒 보호된 페이지")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("접속"):
        if password == "1234":
            st.session_state['login'] = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")

# 로그인 후 보여줄 메인 화면
else:
    st.title("🔓 환영합니다! 이제 메뉴가 보입니다.")
    st.write("왼쪽 사이드바를 확인해 보세요.")
    
    if st.button("로그아웃"):
        st.session_state['login'] = False
        st.rerun()
