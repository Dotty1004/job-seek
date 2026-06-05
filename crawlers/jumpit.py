import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from crawlers.base import BaseCrawler


class JumpitCrawler(BaseCrawler):
    source = "점핏"
    _base_url = "https://www.jumpit.co.kr/search"

    def fetch(self, keyword: str) -> list[dict]:
        rows = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
            )
            page = browser.new_page()
            page.set_extra_http_headers({"Accept-Language": "ko-KR,ko;q=0.9"})

            try:
                page.goto(f"{self._base_url}?keyword={keyword}", timeout=30000)
                page.wait_for_selector('a[href*="/position/"]', timeout=15000)

                prev_height = 0
                for _ in range(8):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.5)
                    curr_height = page.evaluate("document.body.scrollHeight")
                    if curr_height == prev_height:
                        break
                    prev_height = curr_height

                soup = BeautifulSoup(page.content(), "html.parser")
                cards = soup.select('a[href*="/position/"]')

                for card in cards:
                    title_tag = card.select_one("h2.position_card_info_title")
                    img_tag = card.select_one("img.img")
                    company = ""
                    if img_tag and img_tag.get("alt"):
                        company = img_tag["alt"]
                    else:
                        company_div = card.select_one("div.sc-15ba67b8-0 div")
                        company = company_div.get_text(strip=True) if company_div else ""

                    info_items = card.select("ul.coaZDw li")
                    location = info_items[0].get_text(strip=True) if len(info_items) > 0 else ""
                    experience = info_items[1].get_text(strip=True) if len(info_items) > 1 else ""

                    deadline_tag = card.select_one("span.sc-a0b0873a-0")
                    deadline = deadline_tag.get_text(strip=True) if deadline_tag else ""

                    href = card.get("href", "")
                    url = f"https://www.jumpit.co.kr{href}" if href.startswith("/") else href

                    rows.append({
                        "title": title_tag.get_text(strip=True) if title_tag else "",
                        "company": company,
                        "location": location,
                        "experience": experience,
                        "deadline": deadline,
                        "url": url,
                    })

            except Exception as e:
                print(f"[점핏] 오류: {e}")
            finally:
                browser.close()

        return rows
