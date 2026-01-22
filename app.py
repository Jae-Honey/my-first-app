import streamlit as st

# 세션 상태를 이용해 로그인 여부를 기억합니다
if 'login' not in st.session_state:
    st.session_state['login'] = False

if not st.session_state['login']:
    # 로그인 화면
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("접속"):
        if password == "1234": # 여기에 원하는 비밀번호 설정
            st.session_state['login'] = True
            st.rerun() # 화면 새로고침
        else:
            st.error("비밀번호가 틀렸습니다.")
else:
    # 로그인 성공 시 보여줄 진짜 내용
    st.title("🔓 환영합니다! 비밀 페이지입니다.")
    if st.button("로그아웃"):
        st.session_state['login'] = False
        st.rerun()
