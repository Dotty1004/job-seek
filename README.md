# job-crawler

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

> A Claude Code skill that crawls Korean job postings for **any keyword** across major platforms — one command to install, five questions to run.

## Installation

**Mac / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/jootang2/job-crawler/main/install.sh | bash
```

**Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/jootang2/job-crawler/main/install.ps1 | iex
```

The script clones this repo to `~/.claude/skills/job-crawler/`, installs Python dependencies, and sets up the Chromium browser for Playwright. Claude Code automatically picks up the skill on next launch.

## Usage

Open Claude Code and type:
```
/job-crawler
```

Claude will guide you through 5 steps:

| Step | Question | Options |
|------|----------|---------|
| 1 | Keyword | AX / AI Engineer·LLM / Prompt Engineer / AI PM / **Any custom keyword** |
| 2 | Platforms | Wanted / Jumpit / Jobkorea / Saramin (multi-select) |
| 3 | Deadline window | 7 / 14 / 30 days / All |
| 4 | Sort order | By deadline / By company / By platform |
| 5 | Extras | Preview top 5 / Auto-open Excel |

Results are saved to `~/.claude/skills/job-crawler/output/jobs_YYYYMMDD_HHMM.xlsx` with clickable hyperlinks to each posting.

## Supported Platforms

| Platform | Method | Notes |
|----------|--------|-------|
| 원티드 (Wanted) | JSON API | IT/startup-heavy listings |
| 점핏 (Jumpit) | Playwright | Developer-focused |
| 잡코리아 (Jobkorea) | Playwright | Strong in large enterprise |
| 사람인 (Saramin) | REST API | Requires API key (see below) |

## Saramin API Key

Saramin requires a free API key from [https://oapi.saramin.co.kr](https://oapi.saramin.co.kr).

After obtaining a key, open `~/.claude/skills/job-crawler/config.py` and set:

```python
SARAMIN_API_KEY = "your_key_here"
```

## Update

```bash
# Mac/Linux
git -C ~/.claude/skills/job-crawler pull

# Windows (PowerShell)
git -C "$env:USERPROFILE\.claude\skills\job-crawler" pull
```

Or simply re-run the install script — it detects an existing installation and runs `git pull` automatically.

## Requirements

- Python 3.10+
- Git
- Claude Code

---

## 한국어 설명

### 설치

**Mac / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/jootang2/job-crawler/main/install.sh | bash
```

**Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/jootang2/job-crawler/main/install.ps1 | iex
```

설치 스크립트가 이 레포를 `~/.claude/skills/job-crawler/`에 클론하고,  
Python 패키지와 Playwright 브라우저를 자동으로 설치합니다.  
다음 Claude Code 실행 시 `/job-crawler` 스킬이 자동으로 인식됩니다.

### 사용법

Claude Code에서 입력:
```
/job-crawler
```

5단계 질문에 답하면 크롤링이 시작됩니다:

| 단계 | 질문 | 선택지 |
|------|------|--------|
| 1 | 검색 키워드 | AX / AI Engineer·LLM / 프롬프트 엔지니어 / AI 기획·PM / **직접 입력 (어떤 키워드든 가능)** |
| 2 | 검색 플랫폼 | 원티드 / 점핏 / 잡코리아 / 사람인 (복수 선택) |
| 3 | 마감 기간 | 7일 / 14일 / 30일 / 전체 |
| 4 | 정렬 기준 | 마감일 빠른 순 / 회사명 순 / 사이트별 |
| 5 | 추가 옵션 | 결과 미리보기 / 파일 자동 열기 |

결과는 `~/.claude/skills/job-crawler/output/jobs_YYYYMMDD_HHMM.xlsx`에 저장되며,  
공고 제목을 클릭하면 해당 공고 페이지로 바로 이동할 수 있습니다.

### 사람인 API 키 설정

[https://oapi.saramin.co.kr](https://oapi.saramin.co.kr)에서 무료 API 키를 발급받은 후,  
`~/.claude/skills/job-crawler/config.py`를 열어 아래와 같이 설정합니다:

```python
SARAMIN_API_KEY = "발급받은_키_입력"
```

### 업데이트

재설치 스크립트를 실행하거나 직접 pull 하면 됩니다:

```bash
# Mac/Linux
git -C ~/.claude/skills/job-crawler pull

# Windows
git -C "$env:USERPROFILE\.claude\skills\job-crawler" pull
```

## License

MIT
