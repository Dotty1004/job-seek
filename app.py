"""
채용공고 검색 — 웹앱 (Streamlit)

취준생 누구나 링크 하나로 접속해서, 키워드만 입력하면
원티드·점핏·잡코리아·사람인 공고를 실시간으로 검색하고
엑셀로 내려받을 수 있는 화면.

실행(로컬):   streamlit run app.py
배포:         DEPLOY.md 참고 (Streamlit Community Cloud — 무료 공개 URL)
"""

import sys
import subprocess

import streamlit as st
import pandas as pd

import config
from core import (
    run_crawl,
    df_to_excel_bytes,
    SITE_LABELS,
    SITE_NEEDS_BROWSER,
    SITE_NEEDS_KEY,
)

# ──────────────────────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="채용공고 한눈에 검색",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 사람인 키: Streamlit secrets에 있으면 주입 (배포 환경용)
try:
    if "SARAMIN_API_KEY" in st.secrets:
        config.SARAMIN_API_KEY = st.secrets["SARAMIN_API_KEY"]
except Exception:
    pass


@st.cache_resource(show_spinner=False)
def ensure_chromium() -> bool:
    """
    점핏·잡코리아용 Chromium을 준비한다 (앱 프로세스당 1회).
    Streamlit Cloud는 `playwright install`을 자동 실행하지 않으므로 여기서 처리.
    로컬에 이미 설치돼 있으면 빠르게 통과한다.
    """
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            timeout=600,
        )
        return True
    except Exception:
        return False

# 검색 결과를 세션에 보관 (다운로드/재정렬 시 재크롤링 방지)
if "result" not in st.session_state:
    st.session_state.result = None
if "summary" not in st.session_state:
    st.session_state.summary = {}
if "kw" not in st.session_state:
    st.session_state.kw = "AX"


# ──────────────────────────────────────────────────────────────
# 헤더
# ──────────────────────────────────────────────────────────────
st.title("🧭 채용공고 한눈에 검색")
st.markdown(
    "원티드 · 점핏 · 잡코리아 · 사람인 공고를 **한 번에** 모아드려요. "
    "키워드만 입력하고 검색 버튼을 누르세요. 결과는 엑셀로 저장할 수 있어요."
)

# ──────────────────────────────────────────────────────────────
# 키워드 추천 칩 (폼 위에 배치 → 클릭 시 입력칸에 채워짐)
# ──────────────────────────────────────────────────────────────
st.caption("💡 자주 찾는 키워드 — 눌러서 바로 채우기")
PRESETS = ["AX", "AI Engineer", "프롬프트 엔지니어", "데이터 분석", "기획 PM", "백엔드", "프론트엔드", "마케팅"]
chip_cols = st.columns(len(PRESETS))
for col, preset in zip(chip_cols, PRESETS):
    if col.button(preset, use_container_width=True):
        st.session_state.kw = preset

# ──────────────────────────────────────────────────────────────
# 검색 폼
# ──────────────────────────────────────────────────────────────
with st.form("search_form"):
    keyword = st.text_input(
        "🔎 검색 키워드",
        key="kw",
        placeholder="예: AX, AI Engineer, 프롬프트 엔지니어 …  (쉼표로 여러 개)",
        help="여러 키워드는 쉼표(,)로 구분하세요. 예: AX, LLM",
    )

    c1, c2, c3 = st.columns([2, 1, 1])

    with c1:
        site_options = list(SITE_LABELS.keys())

        def _fmt(code: str) -> str:
            label = SITE_LABELS[code]
            if code in SITE_NEEDS_BROWSER:
                label += " (브라우저 필요)"
            elif code in SITE_NEEDS_KEY:
                label += " (API 키 필요)"
            return label

        sites = st.multiselect(
            "📋 검색할 사이트",
            options=site_options,
            default=["wanted", "jumpit", "jobkorea"],
            format_func=_fmt,
            help="원티드는 가장 안정적이에요. '(브라우저 필요)' 사이트는 환경에 따라 느리거나 막힐 수 있어요.",
        )

    with c2:
        period_label = st.radio(
            "🗓️ 마감 기간",
            options=["1주 이내", "2주 이내", "한 달 이내", "전체"],
            index=1,
            help="마감일 기준으로 공고를 거릅니다. (상시채용은 항상 포함)",
        )
        period_map = {"1주 이내": 7, "2주 이내": 14, "한 달 이내": 30, "전체": 365}
        days = period_map[period_label]

    with c3:
        sort_label = st.radio(
            "↕️ 정렬 기준",
            options=["마감일 빠른 순", "회사명 순", "사이트별"],
            index=0,
        )
        sort_map = {"마감일 빠른 순": "deadline", "회사명 순": "company", "사이트별": "source"}
        sort = sort_map[sort_label]

    submitted = st.form_submit_button("🔍 공고 검색", use_container_width=True, type="primary")


# ──────────────────────────────────────────────────────────────
# 검색 실행
# ──────────────────────────────────────────────────────────────
if submitted:
    keywords = [k.strip() for k in keyword.split(",") if k.strip()]

    if not keywords:
        st.warning("⚠️ 검색 키워드를 입력해 주세요.")
    elif not sites:
        st.warning("⚠️ 검색할 사이트를 하나 이상 선택해 주세요.")
    else:
        # 사람인 선택했는데 키 없음 → 미리 안내
        if "saramin" in sites and not config.SARAMIN_API_KEY:
            st.info("ℹ️ 사람인은 API 키가 있어야 검색돼요. 키가 없으면 사람인 결과는 빈 상태로 표시됩니다.")

        # 점핏·잡코리아 선택 시 브라우저(Chromium) 준비 — 최초 1회만 시간 소요
        browser_sites = [s for s in sites if s in SITE_NEEDS_BROWSER]
        if browser_sites:
            labels = ", ".join(SITE_LABELS[s] for s in browser_sites)
            with st.spinner(f"🌐 {labels} 검색용 브라우저 준비 중… (최초 1회 30초~1분 걸릴 수 있어요)"):
                ok = ensure_chromium()
            if not ok:
                st.warning(
                    f"⚠️ 브라우저 준비에 실패해서 {labels} 검색은 건너뛸 수 있어요. "
                    "원티드·사람인 결과는 정상적으로 표시됩니다."
                )

        progress_box = st.status("공고를 모으는 중이에요…", expanded=True)
        site_status = {}

        def progress(name, status, count=None, error=None):
            label = SITE_LABELS.get(name, name)
            with progress_box:
                if status == "start":
                    st.write(f"⏳ **{label}** 검색 중…")
                elif status == "done":
                    site_status[name] = count
                    st.write(f"✅ **{label}** — {count}건 수집")
                elif status == "error":
                    site_status[name] = 0
                    note = ""
                    if name in SITE_NEEDS_BROWSER:
                        note = " (이 환경에서는 브라우저 사이트가 지원되지 않을 수 있어요)"
                    st.write(f"⚠️ **{label}** — 건너뜀{note}")

        result = run_crawl(keywords, sites, days=days, sort=sort, progress=progress)

        progress_box.update(label="검색 완료!", state="complete", expanded=False)

        st.session_state.result = result
        st.session_state.summary = {
            "keywords": keywords,
            "site_status": site_status,
            "total": len(result),
        }


# ──────────────────────────────────────────────────────────────
# 결과 표시
# ──────────────────────────────────────────────────────────────
result = st.session_state.result

if result is not None:
    summary = st.session_state.summary

    if result.empty:
        st.error(
            "😢 조건에 맞는 공고를 찾지 못했어요.\n\n"
            "- 키워드를 더 일반적인 단어로 바꿔보세요 (예: 'AX' → 'AI')\n"
            "- 마감 기간을 '전체'로 넓혀보세요\n"
            "- 다른 사이트를 함께 선택해보세요"
        )
    else:
        st.divider()

        # 요약 지표
        m1, m2 = st.columns([1, 3])
        m1.metric("총 공고", f"{summary['total']}건")
        with m2:
            by_site = result.groupby("source").size().to_dict()
            chips = "  ".join(f"`{s} {n}`" for s, n in by_site.items())
            st.caption("사이트별 수집")
            st.markdown(chips)

        # 엑셀 다운로드
        from datetime import datetime
        fname = f"공고_{'_'.join(summary['keywords'])}_{datetime.now().strftime('%m%d_%H%M')}.xlsx"
        st.download_button(
            "📥 엑셀로 저장",
            data=df_to_excel_bytes(result),
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=False,
        )

        # 결과 표 (링크 클릭 가능)
        display = result.rename(columns={
            "title": "공고 제목",
            "company": "회사",
            "location": "위치",
            "experience": "경력",
            "deadline": "마감일",
            "source": "출처",
            "url": "링크",
        })[["공고 제목", "회사", "위치", "경력", "마감일", "출처", "링크"]]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            height=600,
            column_config={
                "공고 제목": st.column_config.TextColumn(width="large"),
                "링크": st.column_config.LinkColumn(
                    "지원하기", display_text="열기 ↗", width="small"
                ),
            },
        )
else:
    st.divider()
    st.info("👆 키워드를 입력하고 **공고 검색** 버튼을 눌러주세요.")

# 푸터
st.divider()
st.caption(
    "공고 정보는 각 채용 사이트에서 실시간으로 수집됩니다. "
    "마감·상세 조건은 반드시 원본 공고에서 확인하세요."
)
