import time
import requests
from config import REQUEST_DELAY
from crawlers.base import BaseCrawler


class WantedCrawler(BaseCrawler):
    source = "원티드"
    _search_url = "https://www.wanted.co.kr/api/v4/jobs"
    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "wanted-user-country": "KR",
        "wanted-user-language": "ko",
    }

    def fetch(self, keyword: str) -> list[dict]:
        rows = []
        offset = 0
        limit = 100

        while True:
            params = {
                "query": keyword,
                "limit": limit,
                "offset": offset,
                "country": "kr",
                "tag_type_names": "",
            }
            try:
                resp = requests.get(self._search_url, params=params, headers=self._headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"[원티드] 요청 오류: {e}")
                break

            jobs = data.get("data", [])
            if not jobs:
                break

            for job in jobs:
                job_id = job.get("id", "")
                rows.append({
                    "title": job.get("position", ""),
                    "company": job.get("company", {}).get("name", ""),
                    "location": job.get("address", {}).get("location", ""),
                    "experience": job.get("experience_level", ""),
                    "deadline": job.get("due_time", "")[:10] if job.get("due_time") else "상시",
                    "url": f"https://www.wanted.co.kr/wd/{job_id}",
                })

            links = data.get("links", {})
            if not links.get("next"):
                break
            offset += limit
            time.sleep(REQUEST_DELAY)

        return rows
