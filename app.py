import streamlit as st
import datetime

st.divider() # 구분선
st.subheader("📝 방명록")

# 댓글을 저장할 리스트 (임시 저장소)
if "guestbook" not in st.session_state:
    st.session_state.guestbook = []

# 입력창
with st.form("guestbook_form", clear_on_submit=True):
    name = st.text_input("닉네임")
    content = st.text_area("내용")
    submit = st.form_submit_button("남기기")

    if submit and name and content:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        st.session_state.guestbook.append({"name": name, "content": content, "time": now})

# 저장된 댓글 출력
for entry in reversed(st.session_state.guestbook):
    st.write(f"**{entry['name']}** ({entry['time']})")
    st.info(entry['content'])
