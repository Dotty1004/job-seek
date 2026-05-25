from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd


class BaseCrawler(ABC):
    source: str = ""

    def run(self, keywords: list[str]) -> pd.DataFrame:
        rows = []
        for keyword in keywords:
            rows.extend(self.fetch(keyword))
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df = df.drop_duplicates(subset=["url"])
        df["collected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        df["source"] = self.source
        return df[["title", "company", "location", "experience", "deadline", "url", "source", "collected_at"]]

    @abstractmethod
    def fetch(self, keyword: str) -> list[dict]:
        ...

    @staticmethod
    def _empty_row() -> dict:
        return {"title": "", "company": "", "location": "", "experience": "", "deadline": "", "url": ""}
