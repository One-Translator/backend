from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
from prompts import prompt_map

# LangChain imports 추가 (프롬프트 템플릿만 사용)
from langchain_core.prompts import ChatPromptTemplate

from models.translate import TanslateRequest, TranslateResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

app = FastAPI(
    title="쉬운말 변환 서비스 (o4-mini)",
    description="느린학습자를 위한 쉬운말 변환 API - OpenAI o4-mini + Responses API",
    version="1.0.0"
)

def get_user_prompt(text: str) -> str:
    return f"""원문: {text}"""

def create_prompt_template(difficulty: str = "2단계") -> ChatPromptTemplate:
    """난이도에 따른 ChatPromptTemplate 생성"""
    system_prompt = prompt_map.get(difficulty, prompt_map["2단계"])
    
    template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{user_input}")
    ])
    return template

def get_formatted_prompt(text: str, difficulty: str) -> tuple[str, str]:
    """LangChain 체인을 사용해 프롬프트 생성"""
    try:
        # ChatPromptTemplate 체인 생성
        prompt_template = create_prompt_template(difficulty)
        user_input = get_user_prompt(text)
        
        # 체인 실행해서 메시지 생성
        messages = prompt_template.format_messages(user_input=user_input)
        
        # 시스템 프롬프트와 사용자 프롬프트 분리
        system_prompt = messages[0].content
        user_prompt = messages[1].content
        
        return system_prompt, user_prompt
        
    except Exception as e:
        logger.error(f"LangChain 프롬프트 체인 실패: {str(e)}, 기존 방식으로 fallback")
        # 기존 방식으로 fallback
        system_prompt = prompt_map.get(difficulty, prompt_map["2단계"])
        user_prompt = get_user_prompt(text)
        return system_prompt, user_prompt
    
# === OpenAI 클라이언트 초기화 ===
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None
fallback_client = OpenAI(api_key=api_key) if api_key else None

# === API 엔드포인트 ===

@app.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TanslateRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="API 키가 설정되지 않았습니다.")
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="변환할 텍스트를 입력해주세요.")

    # LangChain 체인을 사용해 프롬프트 생성
    system_prompt, user_prompt = get_formatted_prompt(request.text, request.difficulty)
    
    # o4-mini 시도
    if client:
        try:
            logger.info("o4-mini responses API 호출 중...")
            response = client.responses.create(
                model="o4-mini",
                reasoning={
                    "effort": request.reasoning_effort,
                    "summary": "auto"
                },
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            translated_text = None
            for item in response.output:
                if getattr(item, 'type', None) == 'message' and hasattr(item, 'content'):
                    for content in item.content:
                        if getattr(content, 'type', None) == 'output_text':
                            translated_text = content.text.strip()
                            break
                    if translated_text is not None:
                        break
            reasoning_tokens = None
            total_tokens = None
            
            if hasattr(response, 'usage'):
                usage = response.usage
                total_tokens = getattr(usage, 'total_tokens', None)
                if hasattr(usage, 'output_tokens_details'):
                    reasoning_tokens = getattr(usage.output_tokens_details, 'reasoning_tokens', None)
                elif hasattr(usage, 'completion_tokens_details'):
                    reasoning_tokens = getattr(usage.completion_tokens_details, 'reasoning_tokens', None)
            logger.info(f"o4-mini 변환 성공 (reasoning_tokens: {reasoning_tokens})")
            
            return TranslateResponse(
                original=request.text,
                translated=translated_text,
                difficulty=request.difficulty,
                reasoning_effort=request.reasoning_effort,
                reasoning_tokens=reasoning_tokens,
                total_tokens=total_tokens
            )
            
        except Exception as e:
            logger.error(f"o4-mini 실패: {str(e)}")
            
            # fallback으로 gpt-4o-mini 시도
            if fallback_client:
                try:
                    response = fallback_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=1500
                    )
                    
                    translated_text = response.choices[0].message.content.strip()
                    total_tokens = response.usage.total_tokens if response.usage else None
                    logger.info("gpt-4o-mini fallback 성공")
                    return TranslateResponse(
                        original=request.text,
                        converted=translated_text,
                        difficulty=request.difficulty,
                        reasoning_effort="N/A (fallback)",
                        reasoning_tokens=None,
                        total_tokens=total_tokens
                    )
                    
                except Exception as e:
                    logger.error(f"fallback도 실패: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"변환 실패: {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=f"o4-mini 오류: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)