---
name: job-seek
description: This skill should be used when the user asks to "search jobs", "find job postings", "run job crawler", "취업공고 크롤링", "공고 수집", "공고 검색", "채용공고", or wants to collect Korean job listings for any keyword or position.
---

# job-seek

원하는 키워드로 원티드, 잡코리아, 점핏, 사람인에서 채용공고를 수집하여 Excel 파일로 저장한다.

> **웹앱 버전 있음**: 터미널 없이 브라우저에서 쓰고 싶거나 다른 사람에게 공유하려면
> `app.py` (Streamlit 웹앱)를 사용한다. 사용·배포 방법은 `DEPLOY.md` 참고.
> 아래 5단계 CLI 흐름은 Claude Code 안에서 빠르게 엑셀을 뽑을 때 사용한다.

아래 **5단계를 순서대로** 진행한다. 각 단계는 AskUserQuestion 1회로 처리한다.

단, 5단계 질문 **전에 Step 0(환경 준비)을 먼저 수행**한다.

---

## Step 0 — 환경 준비 (최초 1회 / 새 환경)

크롤링 실행에는 외부 Python 패키지와 Chromium 브라우저가 필요하다.
manus 등 매번 초기화되는 샌드박스에서는 **사용자에게 질문하기 전에** 아래를 먼저 처리한다.

`<base_dir>`은 이 스킬 호출 시 상단에 표시된 **`Base directory for this skill:`** 경로를 사용한다.

### 1) 설치 여부 빠르게 확인

```
python -c "import requests, bs4, playwright, pandas, openpyxl; print('deps OK')"
```
(Mac/Linux는 `python3` 사용)

- `deps OK`가 출력되면 → 2)·3) 건너뛰고 **Step 1로 진행**.
- `ModuleNotFoundError`가 나면 → 아래 2)·3)을 실행.

### 2) Python 패키지 설치

```
python -m pip install -r "<base_dir>/requirements.txt"
```

### 3) Playwright용 Chromium 브라우저 설치

점핏·잡코리아 크롤링은 브라우저가 필요하다. 패키지 설치 직후 한 번 실행한다:

```
python -m playwright install chromium
```

> 참고: 위 명령이 권한/네트워크 문제로 실패하면, 사용자에게 "원티드·사람인은 브라우저 없이 동작하니 우선 그 두 곳만으로 진행할 수 있다"고 안내하고 Step 2(플랫폼)에서 조정한다.

설치가 끝나면 **Step 1로 진행**한다.

---

## Step 1 — 키워드

AskUserQuestion으로 아래 질문을 한다:

- question: "어떤 키워드로 공고를 검색할까요?"
- header: "검색 키워드"
- multiSelect: false
- options (4개):
  - label: "AX", description: "AI Transformation 관련 공고 (기본값)"
  - label: "AI Engineer / LLM", description: "AI·ML 엔지니어, 대형 언어 모델"
  - label: "프롬프트 엔지니어", description: "프롬프트 엔지니어링 직무"
  - label: "AI 기획 / AI PM", description: "AI 서비스 기획, PM 포지션"
- Other 선택 시: 사용자가 입력한 텍스트를 그대로 키워드로 사용

응답을 `keywords` 변수에 저장한다.

---

## Step 2 — 플랫폼

AskUserQuestion으로 아래 질문을 한다:

- question: "어떤 플랫폼에서 검색할까요? (복수 선택 가능)"
- header: "검색 플랫폼"
- multiSelect: true
- options (4개):
  - label: "원티드", description: "IT/스타트업 공고 밀도 높음 → wanted"
  - label: "점핏", description: "IT 개발자 특화 플랫폼 → jumpit"
  - label: "잡코리아", description: "대기업 공고 강세 → jobkorea"
  - label: "사람인", description: "API 키 필요 — config.py에 SARAMIN_API_KEY 설정 후 사용 → saramin"

응답에서 각 label의 `→` 뒤 영어 코드를 추출하여 콤마로 연결 → `sites` 변수
예: 원티드 + 점핏 선택 → `sites = "wanted,jumpit"`

---

## Step 3 — 기간

AskUserQuestion으로 아래 질문을 한다:

- question: "마감일 기준을 선택해주세요."
- header: "마감 기간"
- multiSelect: false
- options (4개):
  - label: "1주 이내 (7일)", description: "급히 지원해야 하는 공고만"
  - label: "2주 이내 (14일)", description: "기본값"
  - label: "한 달 이내 (30일)", description: ""
  - label: "전체", description: "마감 지난 공고만 제외, 나머지 전부 포함"

응답 → `days` 변수: 7 / 14 / 30 / 365

---

## Step 4 — 정렬 기준

AskUserQuestion으로 아래 질문을 한다:

- question: "결과를 어떤 기준으로 정렬할까요?"
- header: "정렬 기준"
- multiSelect: false
- options (3개):
  - label: "마감일 빠른 순", description: "급한 공고가 위로. 상시채용은 맨 아래 → deadline"
  - label: "회사명 순", description: "가나다/알파벳 순 → company"
  - label: "사이트별", description: "플랫폼 그룹으로 묶음 → source"

응답에서 `→` 뒤 코드를 추출 → `sort` 변수

---

## Step 5 — 추가 옵션

AskUserQuestion으로 아래 질문을 한다:

- question: "추가 옵션을 선택해주세요. (없으면 그냥 넘어가도 됩니다)"
- header: "추가 옵션"
- multiSelect: true
- options (2개):
  - label: "결과 미리보기", description: "크롤링 완료 후 상위 5개 공고를 채팅창에 표로 출력"
  - label: "파일 자동 열기", description: "저장 완료 후 Excel 파일 자동 실행"

응답 → `preview` (bool), `auto_open` (bool)

---

## 실행

5단계 응답으로 아래 명령을 조립한다.

`<base_dir>`은 이 스킬 호출 시 상단에 표시된 **`Base directory for this skill:`** 경로를 사용한다.

```
python "<base_dir>/main.py" --keywords <keywords> --days <days> --sites <sites> --sort <sort>
```

**Windows 예시:**
```
python "C:\Users\USERNAME\.claude\skills\job-crawler\main.py" --keywords AX --days 14 --sites wanted,jumpit --sort deadline
```

**Mac / Linux 예시:**
```
python3 ~/.claude/skills/job-crawler/main.py --keywords AX --days 14 --sites wanted,jumpit --sort deadline
```

Python 경로를 찾을 수 없으면 `where python` (Windows) 또는 `which python3` (Mac/Linux)으로 확인 후 절대경로 사용.

---

## 결과 처리

실행 완료 후:

1. **항상**: 사이트별 수집 건수 + 총 건수 + xlsx 파일 전체 경로를 보고한다.

2. **미리보기 선택 시**: 수집 결과 상위 5행을 마크다운 표로 출력한다:

   | 공고 제목 | 회사 | 마감일 | 출처 |
   |----------|------|--------|------|
   | ...      | ...  | ...    | ...  |

3. **파일 자동 열기 선택 시**: 아래 명령을 실행한다:
   - Windows: `start "" "<xlsx_path>"`
   - Mac: `open "<xlsx_path>"`
   - Linux: `xdg-open "<xlsx_path>"`

---

## 에러 처리

| 오류 | 원인 | 조치 |
|------|------|------|
| `PermissionError` | xlsx 파일이 열려 있음 | 파일 닫고 재실행 안내 |
| 수집 0건 | 키워드가 좁거나 사이트 차단 | 키워드 변경 또는 플랫폼 조정 안내 |
| `ModuleNotFoundError` | 패키지 미설치 | **Step 0**의 2)·3) 재실행 (`pip install -r "<base_dir>/requirements.txt"`) |
| `playwright ... Executable doesn't exist` / 브라우저 없음 | Chromium 미설치 | **Step 0**의 3) 실행 (`python -m playwright install chromium`) |
| 사람인 0건 | API 키 없음 | `config.py`의 `SARAMIN_API_KEY` 설정 안내 |
