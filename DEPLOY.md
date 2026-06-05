# 채용공고 검색 웹앱 — 사용 & 공유 가이드

취준생 누구나 **링크 하나로 접속**해서 키워드만 입력하면
원티드·점핏·잡코리아·사람인 공고를 실시간으로 검색하고 엑셀로 받을 수 있습니다.

---

## 사용 방법은 3가지

| 방법 | 누구에게 | 난이도 | 결과 |
|------|----------|--------|------|
| **A. 무료 웹 배포** | 많은 사람에게 공유 | ★★☆ (최초 1회) | 공개 URL — 받는 사람은 클릭만 |
| **B. 내 컴퓨터에서 실행** | 나 혼자 / 소수 | ★☆☆ | 더블클릭으로 실행 (Mac) |
| **C. 터미널 실행** | 개발 익숙한 사람 | ★☆☆ | `streamlit run app.py` |

---

## 방법 A — 무료 웹으로 배포 (Streamlit Community Cloud) ⭐ 추천

한 번 배포해두면 **URL만 공유**하면 됩니다. 받는 사람은 설치·터미널 없이 클릭만.

### 준비물
- GitHub 계정 (무료)
- Streamlit 계정 (무료, GitHub로 바로 로그인)

### 순서
1. **GitHub에 코드 올리기**
   - github.com → `New repository` → 이름 예: `job-crawler`
   - 이 폴더(`job-crawler/`)의 파일 전체를 업로드
     (드래그&드롭 업로드 가능: `app.py`, `core.py`, `crawlers/`, `config.py`,
     `requirements.txt`, `packages.txt`)

2. **Streamlit Cloud에서 배포**
   - https://share.streamlit.io 접속 → GitHub로 로그인
   - `Create app` → 방금 만든 저장소 선택
   - **Main file path**: `app.py`
   - `Deploy` 클릭 → 1~3분 후 `https://○○○.streamlit.app` 주소 생성

3. **완성** — 이 주소를 단톡방·커뮤니티에 공유하면 끝!

### (선택) 사람인까지 검색하려면
- https://oapi.saramin.co.kr 에서 무료 API 키 발급
- Streamlit Cloud 앱 → `⋮` → `Settings` → `Secrets`에 입력:
  ```
  SARAMIN_API_KEY = "발급받은키"
  ```

> **점핏·잡코리아도 클라우드에서 동작합니다.**
> 이 두 사이트는 브라우저(Chromium)가 필요한데, 다음이 자동으로 처리됩니다:
> - `packages.txt` — Chromium 시스템 라이브러리 설치
> - 앱이 점핏·잡코리아 검색 시 Chromium을 자동 설치 (**최초 1회 30초~1분 소요**)
> - 크롤러에 `--no-sandbox` 옵션 적용 (클라우드 필수)
>
> 단, **첫 검색**에서 브라우저 준비로 시간이 걸리고, 채용 사이트가
> 클라우드 IP를 일시 차단하면 해당 사이트만 0건이 될 수 있습니다.
> 이 경우에도 **원티드는 항상 안정적으로 동작**합니다.

---

## 방법 B — 내 Mac에서 더블클릭 실행

1. Finder에서 `run_web.command` 더블클릭
2. (최초 1회) 패키지 자동 설치 — 1~2분
3. 브라우저가 자동으로 열립니다

> "확인되지 않은 개발자" 경고가 뜨면:
> `시스템 설정 → 개인정보 보호 및 보안`에서 `확인 없이 열기` 클릭.

---

## 방법 C — 터미널에서 실행 (Mac / Windows / Linux)

```bash
pip install -r requirements.txt
python -m playwright install chromium   # 점핏·잡코리아용 (선택)
streamlit run app.py
```

---

## 기존 CLI도 그대로 동작

엑셀 파일만 빠르게 뽑고 싶을 때:
```bash
python main.py --keywords AX --days 14 --sites wanted,jumpit --sort deadline
```
또는 Claude Code에서 `/job-crawler` 슬래시 커맨드 사용.

---

## 자주 묻는 질문

**Q. 받는 사람도 뭔가 설치해야 하나요?**
방법 A로 배포하면 **아무것도 설치 안 해도** 됩니다. URL 클릭만 하면 됩니다.

**Q. 무료인가요?**
네. Streamlit Community Cloud는 개인용 공개 앱은 무료입니다.

**Q. 검색이 0건이에요.**
키워드를 더 일반적으로(예: 'AX'→'AI'), 기간을 '전체'로, 사이트를 여러 개 선택해보세요.
점핏·잡코리아가 막히는 환경이면 원티드만으로도 충분히 결과가 나옵니다.
