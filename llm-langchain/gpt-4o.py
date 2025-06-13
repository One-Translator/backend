from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import logging

from prompts import prompt_map

from models.translate import TanslateRequest, TranslateResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

app = FastAPI(
    title="쉬운말 변환 서비스 (gpt-4o)",
    description="느린학습자를 위한 쉬운말 변환 API - LangChain + gpt-4o",
    version="1.0.0"
)

def create_prompt_template(level: str = "2단계") -> ChatPromptTemplate:
    system_prompt = prompt_map.get(level, prompt_map["2단계"])

    
    template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{user_input}")
    ])
    return template

def get_user_prompt(text: str) -> str:
    return f"""원문: {text}"""

# === LangChain 모델 초기화 ===
api_key = os.getenv("OPENAI_API_KEY")
llm = None

if api_key:
    try:
        logger.info("OpenAI API 키 확인됨")
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.3,
            max_tokens=1500
        )
    except Exception as e:
        logger.error(f"LangChain 모델 초기화 실패: {e}")
        llm = None
else:
    logger.error("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

# 출력 파서
output_parser = StrOutputParser()

# === API 엔드포인트 ===
@app.post("/translate", response_model=TranslateResponse)

async def translate_text(request: TanslateRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="API 키가 설정되지 않았습니다.")
    if not llm:
        raise HTTPException(status_code=500, detail="gpt-4o-mini 서비스를 사용할 수 없습니다. API 키를 확인해주세요.")

    try:        
        prompt_template = create_prompt_template(request.level)
        
        user_input = get_user_prompt(request.text)

        
        # LangChain 체인 구성 및 실행
        chain = prompt_template | llm | output_parser
        translated_text = await chain.ainvoke({"user_input": user_input})
        
        
        return TranslateResponse(
            original=request.text,
            translated=translated_text.strip(),
            level=request.level,

            reasoning_effort=getattr(request, 'reasoning_effort', "N/A (LangChain)"),
            reasoning_tokens=None,  # LangChain에서는 직접 접근 어려움
            total_tokens=None       # 필요시 콜백으로 추적 가능
        )
        
    except Exception as e:
        logger.error(f"gpt-4o-mini LangChain 체인 실행 실패: {str(e)}")
        logger.error(f"에러 타입: {type(e).__name__}")
        
        if "API key" in str(e):
            raise HTTPException(status_code=500, detail="OpenAI API 키 오류입니다.")
        elif "model" in str(e):
            raise HTTPException(status_code=500, detail="gpt-4o-mini 모델 오류입니다.")
        elif "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail="API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
        else:
            raise HTTPException(status_code=500, detail=f"변환 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)