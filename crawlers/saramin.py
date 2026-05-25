import time
import requests
from config import SARAMIN_API_KEY, REQUEST_DELAY
from crawlers.base import BaseCrawler


class SaraminCrawler(BaseCrawler):
    source = "사람인"
    _base_url = "https://oapi.saramin.co.kr/job-search"

    def fetch(self, keyword: str) -> list[dict]:
        if not SARAMIN_API_KEY:
            print("[사람인] API 키 없음 — config.py의 SARAMIN_API_KEY를 설정하세요.")
            return []

        rows = []
        page = 1
        while True:
            params = {
                "access-key": SARAMIN_API_KEY,
                "keywords": keyword,
                "job_mid_cd": "",
                "count": 100,
                "start": page,
                "fields": "id,position,company,posting-date,expiration-date,close-type,job-url",
            }
            try:
                resp = requests.get(self._base_url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"[사람인] 요청 오류: {e}")
                break

            jobs = data.get("jobs", {}).get("job", [])
            if not jobs:
                break

            for job in jobs:
                pos = job.get("position", {})
                rows.append({
                    "title": pos.get("title", ""),
                    "company": job.get("company", {}).get("detail", {}).get("name", ""),
                    "location": pos.get("location", {}).get("name", ""),
                    "experience": pos.get("experience-level", {}).get("name", ""),
                    "deadline": job.get("expiration-date", ""),
                    "url": job.get("job-url", ""),
                })

            total = int(data.get("jobs", {}).get("total", 0))
            if page * 100 >= total:
                break
            page += 1
            time.sleep(REQUEST_DELAY)

        return rows
