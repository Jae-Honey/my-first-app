# 1. 페이지 설정
st.set_page_config(page_title="정재헌 월드", layout="centered")

# 2. 로그인 세션 및 연결 설정
# 2. 로그인 세션 및 설정
if 'login' not in st.session_state:
st.session_state['login'] = False

conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["connections"]["gsheets"]["spreadsheet"]

# gspread 인증 함수
# gspread 인증 함수 (잔상 방지용 직접 통신)
def get_gspread_client():
creds_info = {
"type": st.secrets["connections"]["gsheets"]["type"],
@@ -31,6 +31,38 @@ def get_gspread_client():
}
return gspread.service_account_from_dict(creds_info)

# 💡 [팝업 함수 1] 방명록 등록 중
@st.dialog("알림", width="small")
def show_saving_dialog(name, content, pw):
    st.write("🚀 **당신의 흔적을 남기는 중입니다!**")
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
    st.write("🗑️ **당신의 흔적이 사라지는 중입니다다!**")
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
st.title("🔒 아무나 못 들어옴옴")
@@ -44,16 +76,6 @@ def get_gspread_client():

# --- 로그인 후 메인 화면 ---
else:
    # 💡 [필살기] 잔상이 보일 수 있는 모든 UI 요소를 CSS로 강제 제어
    st.markdown("""
        <style>
        /* 데이터프레임이나 테이블 형태의 모든 자동 출력을 숨김 */
        div[data-testid="stDataFrameResizer"], 
        div[data-testid="stTable"],
        pre { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

st.title("📝 방명록")

# 데이터 로드
@@ -65,29 +87,22 @@ def load_data():

df = load_data()

    # --- 방명록 작성 폼 ---
    with st.form("guestbook_form", clear_on_submit=True):
    # --- 방명록 작성 폼 (순서 변경: 이름 -> 메시지 -> 비밀번호) ---
    with st.container(border=True):
st.subheader("새 글 남기기")
        name = st.text_input("닉네임")
        pw = st.text_input("삭제 비밀번호", type="password")
        content = st.text_area("메시지")
        submit = st.form_submit_button("등록")

        if submit:
        name = st.text_input("이름", placeholder="닉네임을 입력하세요")
        content = st.text_area("메시지", placeholder="따뜻한 한마디를 남겨주세요")
        pw = st.text_input("비밀번호", type="password", placeholder="삭제 시 필요합니다")
        
        if st.button("방명록 등록", use_container_width=True):
if name and content and pw:
                # 💡 등록 시 즉시 화면을 덮는 스피너 가동
                with st.spinner("방명록을 안전하게 배달 중..."):
                    gc = get_gspread_client()
                    sheet = gc.open_by_url(url).worksheet("sheet1")
                    new_row = [name, content, datetime.now().strftime("%Y-%m-%d %H:%M"), str(pw).strip()]
                    sheet.append_row(new_row)
                    st.cache_data.clear()
                    time.sleep(0.5) # 잔상이 사라질 때까지의 아주 짧은 유예 시간
                st.rerun()
                show_saving_dialog(name, content, pw) # 팝업 호출
            else:
                st.warning("모든 항목을 입력해주세요.")

st.divider()

    # --- 목록 출력 및 삭제 ---
    # --- 목록 출력 ---
if not df.empty:
for i in reversed(range(len(df))):
row = df.iloc[i]
@@ -100,18 +115,11 @@ def load_data():
with st.expander("삭제"):
del_pw = st.text_input("비번", type="password", key=f"pw_{i}")
if st.button("확인", key=f"btn_{i}"):
                            if str(del_pw).strip() == str(row['password']).split('.')[0].strip():
                                with st.spinner("삭제 기록 보관 중..."):
                                    gc = get_gspread_client()
                                    ss = gc.open_by_url(url)
                                    # 백업 및 삭제
                                    ss.worksheet("deleted_logs").append_row(row.tolist())
                                    ss.worksheet("sheet1").delete_rows(i + 2)
                                    st.cache_data.clear()
                                    time.sleep(0.5)
                                st.rerun()
                            stored_pw = str(row['password']).split('.')[0].strip()
                            if str(del_pw).strip() == stored_pw:
                                show_deleting_dialog(row, i) # 팝업 호출
else:
                                st.error("비번 불일치")
                                st.error("불일치")

if st.sidebar.button("로그아웃"):
st.session_state['login'] = False
