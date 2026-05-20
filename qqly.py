import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Cinematic Diary Music API")

# OpenAI API 키 설정 (환경변수나 직접 입력)
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"
client = OpenAI()

# 유저가 보낼 데이터 구조 정의
class DiaryRequest(BaseModel):
    content: str  # 유저가 작성한 일기 내용

# 음악 데이터 모델
class MusicRecommendation(BaseModel):
    title: str
    artist: str
    youtube_url: str
    reason: str

# 최종 응답 구조 정의
class CinematicResponse(BaseModel):
    genre: str          # 매칭된 영화 장르
    mood_color: str     # UI에 사용할 무드 색상 (HEX 코드)
    poster_phrase: str  # 포스터에 들어갈 감성 문구
    tracks: list[MusicRecommendation]

@app.post("/api/recommend", response_model=CinematicResponse)
async def get_music_recommendation(request: DiaryRequest):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="일기 내용을 입력해주세요.")

    # AI에게 줄 프롬프트 작성 (역할 및 출력 형식 지정)
    prompt = f"""
    사용자의 오늘 하루 일기를 읽고, 이를 '한 편의 영화'라고 생각하고 분석해주세요.
    
    [사용자의 일기]
    "{request.content}"
    
    다음 형식의 JSON 데이터로만 정확히 응답해주세요. 다른 설명은 생략하세요:
    {{
        "genre": "매칭되는 영화 장르 (예: 쓸쓸한 느와르, 청춘 로맨스, 힐링 다큐멘터리 등)",
        "mood_color": "이 감정에 어울리는 스마트폰 UI용 HEX 색상 코드 (예: #2C3E50)",
        "poster_phrase": "영화 포스터에 들어갈 법한 감성적인 카피라이트 문구 한 줄",
        "tracks": [
            {{
                "title": "추천 노래 제목 1",
                "artist": "아티스트 이름 1",
                "youtube_url": "https://www.youtube.com/results?search_query=노래제목+아티스트",
                "reason": "이 곡을 추천하는 이유 (영화의 어떤 장면에 해당하므로)"
            }},
            {{
                "title": "추천 노래 제목 2",
                "artist": "아티스트 ...",
                "youtube_url": "...",
                "reason": "..."
            }}
        ]
    }}
    """

    try:
        # OpenAI GPT 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 음악 전문가이자 영화 감독인 감성 분석 AI야."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} # JSON 응답 보장
        )
        
        # 결과 파싱
        result_json = json.loads(response.choices[0].message.content)
        return result_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
