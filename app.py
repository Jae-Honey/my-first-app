import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# 1. 페이지 설정
st.set_page_config(page_title="나의 보안 방명록", layout="centered")

# 💡 [필살기] 잔상 방지용 CSS: 업데이트 시 튀어나오는 데이터프레임 출력을 강제로 숨김
st.markdown("""
    <style>
    /* st.connection의 결과로 출력되는 div 요소를 숨깁니다 */
    div[data-testid="stDataFrameResizer"] { display: none; }
    div[data-testid="stTable"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. 로그인 세션 관리
if 'login' not in st.session_state:
    st.session_state['login'] = False

# --- 로그인 전 화면 ---
if not st.session_state['login']:
    st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)
    st.title("🔒 관리자 인증")
    password = st.text_input("접속 비밀번호를 입력하세요", type="password")
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
        conn = st.connection("gsheets", type=GSheetsConnection)
        
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
                    with st.status("저장 중...", expanded=False) as status:
                        new_row = pd.DataFrame([{
                            "name": name, "content": content,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "password": str(pw).strip()
                        }])
                        updated_df = pd.concat([df, new_row], ignore_index=True)
                        
                        # 💡 업데이트! (CSS가 결과 출력을 가려줄 것입니다)
                        conn.update(worksheet="sheet1", data=updated_df)
                        st.cache_data.clear()
                        status.update(label="저장 완료!", state="complete")
                    time.sleep(0.3)
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
                                    with st.status("삭제 중...", expanded=False) as status:
                                        deleted_row = df.iloc[[i]].copy()
                                        log_df = get_data("deleted_logs")
                                        updated_log = pd.concat([log_df, deleted_row], ignore_index=True)
                                        
                                        # 💡 삭제 및 백업 (CSS가 가려줌)
                                        conn.update(worksheet="deleted_logs", data=updated_log)
                                        new_df = df.drop(i)
                                        conn.update(worksheet="sheet1", data=new_df)
                                        
                                        st.cache_data.clear()
                                        status.update(label="삭제 완료!", state="complete")
                                    time.sleep(0.3)
                                    st.rerun()
                                else:
                                    st.error("비밀번호 불일치")
        else:
            st.write("첫 번째 방명록을 남겨보세요! ✨")

    except Exception as e:
        st.error(f"오류 발생: {e}")

    if st.sidebar.button("로그아웃"):
        st.session_state['login'] = False
        st.rerun()
