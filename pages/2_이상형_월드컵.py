import streamlit as st
import random

st.set_page_config(page_title="음식 8강 월드컵", layout="centered")

# 1. 초기 데이터 설정 (8개의 음식)
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

# 상태 변수 단순화
candidates = st.session_state.candidates
match_idx = st.session_state.match_idx

st.title("🍴 음식 이상형 월드컵")
st.divider()

# 2. 게임 진행 로직
if len(candidates) > 1:
    st.subheader(f"🔥 {st.session_state.round_name} 진행 중 ({match_idx//2 + 1} / {len(candidates)//2})")
    
    col1, col2 = st.columns(2)
    
    # IndexError 방지를 위한 안전장치
    if match_idx < len(candidates):
        # 왼쪽 후보
        with col1:
            c1 = candidates[match_idx]
            st.image(c1['img'], use_container_width=True, caption=c1['name'])
            if st.button(f"{c1['name']} 선택", key=f"btn_{match_idx}", use_container_width=True):
                st.session_state.winners.append(c1)
                st.session_state.match_idx += 2
                st.rerun()

        # 오른쪽 후보
        with col2:
            if match_idx + 1 < len(candidates):
                c2 = candidates[match_idx + 1]
                st.image(c2['img'], use_container_width=True, caption=c2['name'])
                if st.button(f"{c2['name']} 선택", key=f"btn_{match_idx+1}", use_container_width=True):
                    st.session_state.winners.append(c2)
                    st.session_state.match_idx += 2
                    st.rerun()

    # 모든 대진이 끝났을 때 다음 라운드 처리
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

# 3. 최종 우승자 발표
else:
    st.balloons()
    st.success("🎉 월드컵이 종료되었습니다!")
    st.header(f"🏆 당신의 최종 선택: {candidates[0]['name']}!")
    st.image(candidates[0]['img'], use_container_width=True)
    
    if st.button("처음부터 다시 하기", use_container_width=True):
        # 모든 세션 상태 초기화
        for key in ['candidates', 'winners', 'match_idx', 'round_name']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
