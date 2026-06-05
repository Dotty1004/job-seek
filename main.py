import sys
import argparse
from datetime import datetime
from pathlib import Path

import config
from core import run_crawl, save_excel, SITE_LABELS, CRAWLERS


def parse_args():
    parser = argparse.ArgumentParser(description="job-crawler: 채용공고 수집기")
    parser.add_argument(
        "--keywords", type=str, default=None,
        help="콤마 구분 키워드 (예: AX,LLM). 미지정 시 config.KEYWORDS 사용",
    )
    parser.add_argument(
        "--days", type=int, default=14,
        help="마감일 필터: n일 이내 공고만 수집 (기본값: 14, 365=전체)",
    )
    parser.add_argument(
        "--sites", type=str, default=None,
        help="실행할 사이트 콤마 구분 (예: wanted,jumpit). 미지정 시 config.SITES 사용",
    )
    parser.add_argument(
        "--sort", type=str, default="deadline",
        choices=["deadline", "company", "source"],
        help="정렬 기준: deadline(마감일 빠른 순), company(회사명), source(사이트별)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else config.KEYWORDS
    active_sites = (
        [s.strip() for s in args.sites.split(",")] if args.sites
        else [name for name, on in config.SITES.items() if on]
    )

    print(f"키워드: {keywords}")
    print(f"사이트: {[SITE_LABELS.get(s, s) for s in active_sites]}")
    print(f"마감 필터: {'전체 (마감 지난 공고만 제외)' if args.days >= 365 else f'{args.days}일 이내'}")
    print(f"정렬: {args.sort}")

    def progress(name, status, count=None, error=None):
        label = SITE_LABELS.get(name, name)
        if status == "start":
            print(f"\n{'='*40}\n[{label}] 크롤링 시작 - 키워드 {len(keywords)}개")
        elif status == "done":
            print(f"[{label}] 수집 완료: {count}건")
        elif status == "error":
            print(f"[{label}] 오류로 건너뜀: {error}")

    result = run_crawl(keywords, active_sites, days=args.days, sort=args.sort, progress=progress)

    if result.empty:
        print("\n수집된 데이터가 없습니다.")
        sys.exit(0)

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"jobs_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    save_excel(result, out_path)

    print(f"\n저장 완료: {out_path}")
    print(f"총 {len(result)}건 (사이트별: {result.groupby('source').size().to_dict()})")


if __name__ == "__main__":
    main()
