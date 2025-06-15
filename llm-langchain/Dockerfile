FROM python:3.11-slim

WORKDIR /llm-api

# 의존성 파일 속사
COPY requirements.txt .

RUN pip install -r requirements.txt

# 소스코드 복사
COPY . .

# 컨테이너가 8081 포트 사용하겠다고 알림
EXPOSE 8081

CMD ["python", "gpt-4o.py"]
# CMD ["python", "o4-mini.py"]