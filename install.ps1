$ErrorActionPreference = "Stop"

$skillDir = "$env:USERPROFILE\.claude\skills\job-crawler"
$repoUrl = "https://github.com/jootang2/job-crawler"

Write-Host ""
Write-Host "===============================" -ForegroundColor Cyan
Write-Host "  job-crawler 설치" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# git 확인
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ git이 필요합니다. https://git-scm.com 에서 설치해주세요." -ForegroundColor Red
    exit 1
}

# Python 확인
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $python = $cmd
        break
    }
}
if (-not $python) {
    Write-Host "❌ Python 3.10+ 이 필요합니다. https://python.org 에서 설치해주세요." -ForegroundColor Red
    exit 1
}

$pythonVersion = & $python --version 2>&1
Write-Host "Python: $pythonVersion"

# Clone 또는 업데이트
if (Test-Path "$skillDir\.git") {
    Write-Host ""
    Write-Host "이미 설치되어 있습니다. 최신 버전으로 업데이트 중..."
    git -C $skillDir pull
} else {
    Write-Host ""
    Write-Host "설치 경로: $skillDir"
    New-Item -ItemType Directory -Force -Path (Split-Path $skillDir) | Out-Null
    git clone $repoUrl $skillDir
}

# 패키지 설치
Write-Host ""
Write-Host "패키지 설치 중..."
& $python -m pip install -r "$skillDir\requirements.txt" --quiet

# Playwright 브라우저 설치
Write-Host "브라우저 설치 중..."
& $python -m playwright install chromium

Write-Host ""
Write-Host "===============================" -ForegroundColor Green
Write-Host "  설치 완료!" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host ""
Write-Host "Claude Code에서 /job-crawler 를 입력하면 시작됩니다." -ForegroundColor Green
Write-Host ""
