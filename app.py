import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import gspread
import time

# 1. 페이지 설정
st.set_page_config(page_title="정재헌월드", layout="centered")

# 2. 로그인 세션 및 설정
if 'login' not in st.session_state:
    st.session_state['login'] = False

conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["connections"]["gsheets"]["spreadsheet"]

# gspread 인증 함수 (잔상 방지용 직접 통신)
def get_gspread_client():
    creds_info = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
    }
    return gspread.service_account_from_dict(creds_info)

# 💡 [팝업 함수 1] 방명록 등록 중
@st.dialog("알림", width="small")
def show_saving_dialog(name, content, pw):
    st.write("🚀 **올리는 중!**")
    st.progress(50) # 진행 바 표시
    
    # 실제 저장 로직
    gc = get_gspread_client()
    sheet = gc.open_by_url(url).worksheet("sheet1")
    new_row = [name, content, datetime.now().strftime("%Y-%m-%d %H:%M"), str(pw).strip()]
    sheet.append_row(new_row)
    
    st.cache_data.clear()
    time.sleep(0.5)
    st.rerun()

# 💡 [팝업 함수 2] 방명록 삭제 중
@st.dialog("알림", width="small")
def show_deleting_dialog(row_data, row_index):
    st.write("🗑️ **삭제하는 중!**")
    st.progress(50)
    
    # 실제 삭제 로직
    gc = get_gspread_client()
    ss = gc.open_by_url(url)
    ss.worksheet("deleted_logs").append_row(row_data.tolist())
    ss.worksheet("sheet1").delete_rows(row_index + 2)
    
    st.cache_data.clear()
    time.sleep(0.5)
    st.rerun()

# --- 로그인 전 화면 ---
if not st.session_state['login']:
    st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)
    st.title("🔒 아무나 못 들어옴!")
    
    password = st.text_input("비밀번호가 뭘까요? 힌트는 생일", type="password")
    
    if st.button("접속"):
        if password == "0407":
            st.session_state['login'] = True
            st.rerun()
        else:
            st.error("틀렸다.")
            st.image("https://ojsfile.ohmynews.com/down/images/1/animalpark_325244_2[541706].jpg", 
                     caption="출입 금지! 비밀번호를 확인하세요.", width=300)

# --- 로그인 후 메인 화면 ---
else:
    st.title("📝 방명록")

    # 데이터 로드
    def load_data():
        data = conn.read(worksheet="sheet1", ttl=0)
        if data is not None and not data.empty:
            return data.astype(str).replace(r'\.0$', '', regex=True)
        return pd.DataFrame(columns=["name", "content", "date", "password"])

    df = load_data()

    # --- 방명록 작성 폼 (순서 변경: 이름 -> 메시지 -> 비밀번호) ---
    with st.container(border=True):
        st.subheader("새 글 남기기")
        name = st.text_input("이름", placeholder="닉네임을 입력하세요")
        content = st.text_area("메시지", placeholder="따뜻한 한마디를 남겨주세요")
        pw = st.text_input("비밀번호", type="password", placeholder="삭제 시 필요합니다")
        
        if st.button("방명록 등록", use_container_width=True):
            if name and content and pw:
                show_saving_dialog(name, content, pw) # 팝업 호출
            else:
                st.warning("모든 항목을 입력해주세요.")

    st.divider()

    # --- 목록 출력 ---
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
                                show_deleting_dialog(row, i) # 팝업 호출
                            else:
                                st.error("불일치")
    
    if st.sidebar.button("로그아웃"):
        st.session_state['login'] = False
        st.rerun()
