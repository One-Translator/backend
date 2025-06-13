from pydantic import BaseModel
from typing import Optional

class TanslateRequest(BaseModel):
    text: str
    level: str = "2단계" # 디폴트 2단계

    reasoning_effort: str = "medium"

class TranslateResponse(BaseModel):
    original: str
    translated: str
    level: str

    reasoning_effort: str
    reasoning_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
