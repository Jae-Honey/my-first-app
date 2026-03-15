import streamlit as st
import random
import time

# 1. 페이지 기본 설정
st.set_page_config(page_title="음식 8강 월드컵", layout="centered")

# 2. 이미지 크기 고정 및 디자인 CSS
st.markdown("""
    <style>
    /* 이미지 높이 고정 및 비율 유지 */
    [data-testid="stImage"] img {
        height: 300px !important;
        object-fit: cover !important;
        border-radius: 15px;
    }
    /* 버튼 중앙 정렬 및 여백 */
    .stButton button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 초기화 (세션 상태)
if 'candidates' not in st.session_state:
    st.session_state.candidates = [
        {"name": "바삭한 치킨", "img": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500"},
        {"name": "매콤한 떡볶이", "img": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=500"},
        {"name": "육즙 가득 삼겹살", "img": "https://images.unsplash.com/photo-1533245232121-89db38120ee1?w=500"},
        {"name": "신선한 초밥", "img": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=500"},
        {"name": "치즈 듬뿍 피자", "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500"},
        {"name": "얼큰한 짬뽕", "img": "https://images.unsplash.com/photo-1552611052-33e04de081de?w=500"},
        {"name": "달콤한 디저트", "img": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=500"},
        {"name": "든든한 국밥", "img": "https://images.unsplash.com/photo-1608500218890-c4f93a65268d?w=500"}
    ]
    random.shuffle(st.session_state.candidates)
    st.session_state.winners = []
    st.session_state.match_idx = 0
    st.session_state.round_name = "8강"
    st.session_state.total_rounds = 7 # 8강일 때 총 경기 수는 7경기 (4+2+1)
    st.session_state.current_game_count = 0

# 상단 제목
st.title("🍴 음식 이상형 월드컵")

# 4. 게임 진행 섹션
if len(st.session_state.candidates) > 1:
    # 진행도 표시 (Progress Bar)
    progress = st.session_state.current_game_count / st.session_state.total_rounds
    st.progress(progress)
    st.write(f"**진행 상황: {st.session_state.round_name} ({st.session_state.match_idx//2 + 1} / {len(st.session_state.candidates)//2})**")
    st.divider()

    col1, col2 = st.columns(2)
    
    match_idx = st.session_state.match_idx
    candidates = st.session_state.candidates

    # 대진표 안전 확인
    if match_idx + 1 < len(candidates):
        # 왼쪽 후보
        with col1:
            c1 = candidates[match_idx]
            st.image(c1['img'], use_container_width=True)
            if st.button(f"선택: {c1['name']}", key=f"c1_{match_idx}"):
                st.session_state.winners.append(c1)
                st.session_state.match_idx += 2
                st.session_state.current_game_count += 1
                st.rerun()

        # 오른쪽 후보
        with col2:
            c2 = candidates[match_idx + 1]
            st.image(c2['img'], use_container_width=True)
            if st.button(f"선택: {c2['name']}", key=f"c2_{match_idx}"):
                st.session_state.winners.append(c2)
                st.session_state.match_idx += 2
                st.session_state.current_game_count += 1
                st.rerun()

    # 다음 라운드 진출 로직
    if st.session_state.match_idx >= len(candidates):
        st.session_state.candidates = st.session_state.winners
        st.session_state.winners = []
        st.session_state.match_idx = 0
        
        # 라운드 이름 업데이트
        if len(st.session_state.candidates) == 4:
            st.session_state.round_name = "4강"
        elif len(st.session_state.candidates) == 2:
            st.session_state.round_name = "결승전"
        st.rerun()

# 5. 최종 결과 섹션
else:
    st.balloons()
    st.success("🎉 모든 대결이 끝났습니다!")
    st.header(f"🏆 당신이 선택한 최고의 음식: {st.session_state.candidates[0]['name']}")
    st.image(st.session_state.candidates[0]['img'], use_container_width=True)
    
    st.divider()
    if st.button("다시 시작하기"):
        # 초기화 시 모든 세션 데이터 삭제
        for key in ['candidates', 'winners', 'match_idx', 'round_name', 'current_game_count']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
