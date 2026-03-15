import streamlit as st
import random

st.set_page_config(page_title="이상형 월드컵", layout="centered")

# 1. 후보 데이터 (이름과 이미지 URL)
if 'candidates' not in st.session_state:
    st.session_state.candidates = [
        {"name": "피자", "img": "https://placekitten.com/300/300"},
        {"name": "치킨", "img": "https://placekitten.com/301/301"},
        {"name": "삼겹살", "img": "https://placekitten.com/302/302"},
        {"name": "초밥", "img": "https://placekitten.com/303/303"},
    ]
    random.shuffle(st.session_state.candidates)
    st.session_state.winners = []
    st.session_state.round_count = 0

# 2. 게임 로직 제어 변수
if 'current_match' not in st.session_state:
    st.session_state.current_match = 0

candidates = st.session_state.candidates
match_idx = st.session_state.current_match

st.title("🏆 음식 이상형 월드컵")

# 3. 게임 진행 화면
if len(candidates) > 1:
    st.subheader(f"{len(candidates) * 2 if st.session_state.round_count == 0 else len(candidates)}강 진행 중!")
    
    col1, col2 = st.columns(2)
    
    # 왼쪽 후보
    with col1:
        c1 = candidates[match_idx]
        st.image(c1['img'], use_column_width=True)
        if st.button(c1['name'], key="btn1"):
            st.session_state.winners.append(c1)
            st.session_state.current_match += 2
            st.rerun()

    # 오른쪽 후보
    with col2:
        c2 = candidates[match_idx + 1]
        st.image(c2['img'], use_column_width=True)
        if st.button(c2['name'], key="btn2"):
            st.session_state.winners.append(c2)
            st.session_state.current_match += 2
            st.rerun()

    # 다음 라운드 진출 판단
    if st.session_state.current_match >= len(candidates):
        st.session_state.candidates = st.session_state.winners
        st.session_state.winners = []
        st.session_state.current_match = 0
        st.session_state.round_count += 1
        st.rerun()

# 4. 최종 우승자 발표
else:
    st.balloons()
    st.header(f"✨ 최종 우승: {candidates[0]['name']}! ✨")
    st.image(candidates[0]['img'], width=400)
    
    if st.button("다시 하기"):
        del st.session_state.candidates
        del st.session_state.current_match
        st.rerun()
