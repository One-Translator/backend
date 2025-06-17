# 스크립트는 항상 루트에서 실행

echo "🧼 기존 컨테이너 정리 중..."
docker compose --env-file .env.dev -f ./dev/compose.yml down --volumes --remove-orphans

echo "🚀 컨테이너 실행 중..."
docker compose --env-file .env.dev -f ./dev/compose.yml up -d

echo "✅ 개발 환경 실행 완료!"