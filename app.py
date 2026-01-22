import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# (로그인 로직 이후 메인 화면 부분)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="sheet1", ttl=0)

    # 데이터프레임이 비어있을 경우 초기화
    if df is None or df.empty:
        df = pd.DataFrame(columns=["name", "content", "date", "password"])

    st.subheader("📝 방명록 남기기")
    with st.form("guestbook_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("닉네임")
        with col2:
            pw = st.text_input("삭제 비밀번호", type="password", help="글을 지울 때 필요해요!")
        
        content = st.text_area("메시지")
        submit = st.form_submit_button("남기기")

        if submit:
            if name and content and pw:
                new_data = pd.DataFrame([{
                    "name": name,
                    "content": content,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "password": str(pw) # 비밀번호 저장
                }])
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(worksheet="sheet1", data=updated_df)
                st.success("방명록이 저장되었습니다!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.warning("모든 칸을 채워주세요.")

    st.divider()
    st.subheader("💬 방명록 목록")

    # 최신순으로 출력
    for i, row in df.iloc[::-1].iterrows():
        with st.container():
            col_text, col_del = st.columns([0.8, 0.2])
            
            with col_text:
                st.write(f"**{row['name']}** ({row['date']})")
                st.info(row['content'])
            
            with col_del:
                # 각 글마다 고유한 팝업창(expander) 생성
                with st.expander("삭제"):
                    del_pw = st.text_input("비밀번호", type="password", key=f"del_{i}")
                    if st.button("확인", key=f"btn_{i}"):
                        if str(del_pw) == str(row['password']):
                            # 해당 행 제외하고 다시 저장
                            new_df = df.drop(i)
                            conn.update(worksheet="sheet1", data=new_df)
                            st.success("삭제되었습니다!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("불일치")
