import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from crawlers.base import BaseCrawler


class RocketpunchCrawler(BaseCrawler):
    source = "로켓펀치"
    _base_url = "https://www.rocketpunch.com/jobs"

    def fetch(self, keyword: str) -> list[dict]:
        rows = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(f"{self._base_url}?keywords={keyword}", timeout=30000)
                page.wait_for_selector("div.job.item", timeout=15000)

                prev_height = 0
                for _ in range(6):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.5)
                    curr_height = page.evaluate("document.body.scrollHeight")
                    if curr_height == prev_height:
                        break
                    prev_height = curr_height

                soup = BeautifulSoup(page.content(), "html.parser")
                items = soup.select("div.job.item")

                for item in items:
                    title_tag = item.select_one("h4.header a.job-title")
                    company_tag = item.select_one("a.company-name")
                    loc_tag = item.select_one("span.location")
                    exp_tag = item.select_one("span.experience")
                    deadline_tag = item.select_one("span.deadline")

                    href = title_tag["href"] if title_tag and title_tag.get("href") else ""
                    url = f"https://www.rocketpunch.com{href}" if href.startswith("/") else href

                    rows.append({
                        "title": title_tag.get_text(strip=True) if title_tag else "",
                        "company": company_tag.get_text(strip=True) if company_tag else "",
                        "location": loc_tag.get_text(strip=True) if loc_tag else "",
                        "experience": exp_tag.get_text(strip=True) if exp_tag else "",
                        "deadline": deadline_tag.get_text(strip=True) if deadline_tag else "",
                        "url": url,
                    })

            except Exception as e:
                print(f"[로켓펀치] 오류: {e}")
            finally:
                browser.close()

        return rows
