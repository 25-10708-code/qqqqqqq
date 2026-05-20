import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(
    title="시네마틱 다이어리 음악 추천 API",
    description="사용자의 일기를 분석해 영화 장르와 OST를 추천하는 API입니다.",
    version="1.0.0"
)

# [중요] OpenAI API Key 설정
# Streamlit Cloud의 Settings -> Secrets에 OPENAI_API_KEY를 등록하는 것이 가장 안전합니다.
# 임시 테스트용이라면 아래 주석을 풀고 직접 입력하셔도 됩니다.
# os.environ["OPENAI_API_KEY"] = "your-actual-api-key"

# OpenAI 클라이언트 초기화 (환경변수나 Secrets에서 자동으로 Key를 읽어옵니다)
try:
    client = OpenAI()
except Exception:
    # API Key가 없을 경우를 대비한 가이드
    client = None

# 요청 데이터 구조 정의
class DiaryRequest(BaseModel):
    content: str

# 응답 데이터 구조 정의
class MusicRecommendation(BaseModel):
    title: str
    artist: str
    youtube_url: str
    reason: str

class CinematicResponse(BaseModel):
    genre: str
    mood_color: str
    poster_phrase: str
    tracks: list[MusicRecommendation]

@app.get("/")
def read_root():
    return {
        "message": "시네마틱 다이어리 API 서버가 정상 작동 중입니다!",
        "api_docs": "테스트를 원하시면 주소 뒤에 /docs 를 붙여서 접속해주세요 (예: xxx.streamlit.app/docs)"
    }

@app.post("/api/recommend", response_model=CinematicResponse)
async def get_music_recommendation(request: DiaryRequest):
    if not client or not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API Key가 설정되지 않았습니다. 서버 설정을 확인해주세요."
        )
        
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="일기 내용을 입력해주세요.")

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
                "artist": "아티스트 이름 2",
                "youtube_url": "https://www.youtube.com/results?search_query=노래제목+아티스트",
                "reason": "이 곡을 추천하는 이유"
            }}
        ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 음악 전문가이자 영화 감독인 감성 분석 AI야."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result_json = json.loads(response.choices[0].message.content)
        return result_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 중 오류가 발생했습니다: {str(e)}")
