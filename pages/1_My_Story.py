# pages/1_My_Story.py 파일 상단
import streamlit as st

if 'login' not in st.session_state or not st.session_state['login']:
    st.error("먼저 메인 페이지에서 로그인해 주세요!")
    st.stop() # 이후 코드를 실행하지 않고 멈춤

st.title("여기는 상세 페이지입니다.")
