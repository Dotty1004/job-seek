import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from crawlers.base import BaseCrawler


class JobkoreaCrawler(BaseCrawler):
    source = "잡코리아"
    _base_url = "https://www.jobkorea.co.kr/Search/"

    def fetch(self, keyword: str) -> list[dict]:
        rows = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(f"{self._base_url}?stext={keyword}", timeout=30000)
                page.wait_for_selector('div[data-sentry-component="CardJob"]', timeout=15000)
                time.sleep(2)

                soup = BeautifulSoup(page.content(), "html.parser")
                cards = soup.select('div[data-sentry-component="CardJob"]')

                for card in cards:
                    title_tag = card.select_one('a[data-sentry-component="Title"] span.font-semibold')
                    title_link = card.select_one('a[data-sentry-component="Title"]')
                    company_tag = card.select_one('span.truncate.text-gray700')
                    chips = card.select('div[data-sentry-component="GrayChip"] span.text-gray900')
                    exp_tag = card.select_one('span.flex-shrink-0.text-gray700.text-typo-c1-13')
                    deadline_tag = next(
                        (s for s in card.select('span.text-typo-c1-13.text-gray700') if '마감' in s.get_text()),
                        None,
                    )

                    url = title_link["href"] if title_link and title_link.get("href") else ""

                    rows.append({
                        "title": title_tag.get_text(strip=True) if title_tag else "",
                        "company": company_tag.get_text(strip=True) if company_tag else "",
                        "location": chips[0].get_text(strip=True) if chips else "",
                        "experience": exp_tag.get_text(strip=True) if exp_tag else "",
                        "deadline": deadline_tag.get_text(strip=True).replace(" 마감", "") if deadline_tag else "",
                        "url": url,
                    })

            except Exception as e:
                print(f"[잡코리아] 오류: {e}")
            finally:
                browser.close()

        return rows
