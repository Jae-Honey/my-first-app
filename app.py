import streamlit as st

st.title("나의 첫 배포 웹사이트!")
st.write("이 사이트는 컴퓨터를 꺼도 계속 유지됩니다.")

name = st.text_input("이름을 입력해주세요:")
if name:
  st.success(f"{name}님, 환영합니다!")
  
