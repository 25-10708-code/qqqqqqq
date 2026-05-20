import streamlit as st
import json
from openai import OpenAI

# 1. 페이지 기본 설정 및 디자인 (감성적인 다크 모드 풍)
st.set_page_config(page_title="시네마틱 다이어리", page_icon="🎬", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #111216; color: #ffffff; }
    .stButton>button { background-color: #E50914; color: white; border-radius: 8px; width: 100%; }
    .movie-card { border: 1px solid #333; padding: 20px; border-radius: 12px; background-color: #1c1d24; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 시네마틱 다이어리")
st.subheader("오늘 당신의 하루는 어떤 영화였나요?")
st.caption("오늘 있었던 일이나 기분을 적으면, AI가 영화 장르로 분석하고 딱 맞는 OST를 추천해 드립니다.")

# 2. OpenAI API 키 설정 (본인의 API 키를 입력하세요)
# 예: client = OpenAI(api_key="sk-xxxx...")
# 테스트를 위해 안전하게 입력받거나 환경변수를 사용하세요.
api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    # 3. 유저 입력창
    user_diary = st.text_area("오늘의 한 줄 일기", placeholder="예: 오늘 비가 오는데 출근길부터 기분이 꿀꿀했어. 회사에서도 실수해서 한 소리 들음.. 소주 당긴다.")

    if st.button("내 하루의 OST 찾기"):
        if not user_diary.strip():
            st.warning("일기 내용을 입력해주세요!")
        else:
            with st.spinner("AI 감독이 당신의 하루를 영화로 제작 중입니다..."):
                prompt = f"""
                사용자의 오늘 하루 일기를 읽고, 이를 '한 편의 영화'라고 생각하고 분석해주세요.
                
                [사용자의 일기]
                "{user_diary}"
                
                다음 형식의 JSON 데이터로만 정확히 응답해주세요. 다른 설명은 생략하세요:
                {{
                    "genre": "매칭되는 영화 장르 (예: 쓸쓸한 느와르, 청춘 로맨스, 힐링 다큐멘터리 등)",
                    "poster_phrase": "영화 포스터에 들어갈 법한 감성적인 카피라이트 문구 한 줄",
                    "tracks": [
                        {{
                            "title": "추천 노래 제목 1",
                            "artist": "아티스트 이름 1",
                            "youtube_url": "https://www.youtube.com/results?search_query=노래제목+아티스트",
                            "reason": "이 곡을 추천하는 이유"
                        }},
                        {{
                            "title": "추천 노래 제목 2",
                            "artist": "아티스트 이름 2",
                            "youtube_url": "https://www.youtube.com/results?search_query=노래제목+아티스트",
                            "reason": "이 곡을 추천하는 이유"
                        }}
                    ]
                }}
                """
                try:
                    # OpenAI 호출
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "너는 음악 전문가이자 영화 감독인 감성 분석 AI야."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    # 4. 결과 화면 시각화
                    st.success("🎬 분석 완료!")
                    
                    # 영화 포스터 스타일 카드
                    st.markdown(f"""
                    <div class="movie-card">
                        <h4 style='color: #E50914;'>TODAY'S GENRE</h4>
                        <h2>🍿 {result['genre']}</h2>
                        <hr style='border-color: #333;'>
                        <p style='font-style: italic; font-size: 1.2rem; color: #bbb;'>"{result['poster_phrase']}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 추천 음악 리스트 출력
                    st.subheader("🎵 오늘의 추천 OST")
                    for track in result['tracks']:
                        with st.expander(f"📌 {track['title']} - {track['artist']}"):
                            st.write(f"**감독의 코멘트:** {track['reason']}")
                            st.video(track['youtube_url']) # 유튜브 검색 링크를 플레이어로 띄우기 시도 (안될 경우 링크 버튼 대체 가능)

                except Exception as e:
                    st.error(f"오류가 발생했습니다. 터미널의 에러 로그를 확인해보세요! \n 에러 내용: {e}")
else:
    st.info("앱을 사용하려면 OpenAI API Key를 먼저 입력해주세요.")
