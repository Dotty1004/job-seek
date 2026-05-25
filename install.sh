#!/bin/bash
set -e

SKILL_DIR="$HOME/.claude/skills/job-crawler"
REPO_URL="https://github.com/jootang2/job-crawler"

echo ""
echo "==============================="
echo "  job-crawler 설치"
echo "==============================="
echo ""

# git 확인
if ! command -v git &> /dev/null; then
    echo "❌ git이 필요합니다. https://git-scm.com 에서 설치해주세요."
    exit 1
fi

# Python 확인
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &> /dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python 3.10+ 이 필요합니다. https://python.org 에서 설치해주세요."
    exit 1
fi

echo "Python: $($PYTHON --version)"

# Clone 또는 업데이트
if [ -d "$SKILL_DIR/.git" ]; then
    echo ""
    echo "이미 설치되어 있습니다. 최신 버전으로 업데이트 중..."
    git -C "$SKILL_DIR" pull
else
    echo ""
    echo "설치 경로: $SKILL_DIR"
    mkdir -p "$(dirname "$SKILL_DIR")"
    git clone "$REPO_URL" "$SKILL_DIR"
fi

# 패키지 설치
echo ""
echo "패키지 설치 중..."
$PYTHON -m pip install -r "$SKILL_DIR/requirements.txt" --quiet

# Playwright 브라우저 설치
echo "브라우저 설치 중..."
$PYTHON -m playwright install chromium

echo ""
echo "==============================="
echo "  설치 완료!"
echo "==============================="
echo ""
echo "Claude Code에서 /job-crawler 를 입력하면 시작됩니다."
echo ""
