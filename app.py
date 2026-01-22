import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 구글 시트 연결 (설정은 Streamlit Cloud에서 할 예정)
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📖 영구 저장 방명록")

# 1. 기존 댓글 읽어오기
try:
    data = conn.read(worksheet="sheet1")
except Exception as e:
    # 만약 시트가 비어있어서 에러가 난다면, 빈 틀을 만듭니다.
    data = pd.DataFrame(columns=["name", "content", "date"])

# 2. 입력 창
with st.form("guestbook"):
    name = st.text_input("닉네임")
    content = st.text_area("내용")
    if st.form_submit_button("남기기"):
        # 새 데이터 한 줄 만들기
        new_row = pd.DataFrame([{"name": name, "content": content, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}])
        # 기존 데이터에 합치기
        updated_df = pd.concat([data, new_row], ignore_index=True)
        # 구글 시트에 다시 쓰기
        conn.update(worksheet="ｓheet1", data=updated_df)
        st.success("글이 저장되었습니다!")
        st.rerun()

# 3. 화면에 출력
st.divider()
for i, row in data.iterrows():
    st.write(f"**{row['name']}** ({row['date']})")
    st.info(row['content'])
