#!/bin/bash
# 더블클릭하면 채용공고 검색 웹앱이 브라우저에서 열립니다 (Mac 전용).
# 처음 실행 시 필요한 패키지를 자동으로 설치합니다.

cd "$(dirname "$0")" || exit 1

echo "================================"
echo "  채용공고 검색 웹앱 시작 준비"
echo "================================"

# python3 확인
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 이 설치되어 있지 않습니다."
  echo "   https://www.python.org/downloads/ 에서 설치 후 다시 실행하세요."
  read -r -p "엔터를 누르면 종료합니다..."
  exit 1
fi

# 의존성 확인 / 설치
if ! python3 -c "import streamlit, requests, bs4, pandas, openpyxl" >/dev/null 2>&1; then
  echo "📦 필요한 패키지를 설치합니다 (처음 한 번만, 1~2분 소요)..."
  python3 -m pip install -r requirements.txt
fi

# 브라우저 사이트(점핏·잡코리아)용 Chromium — 실패해도 원티드는 동작
python3 -c "import playwright" >/dev/null 2>&1 && python3 -m playwright install chromium >/dev/null 2>&1

echo "🚀 웹앱을 엽니다... 브라우저가 자동으로 열립니다."
echo "   (종료하려면 이 창에서 Ctrl + C)"
python3 -m streamlit run app.py
