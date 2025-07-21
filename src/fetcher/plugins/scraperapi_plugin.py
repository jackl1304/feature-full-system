# src/fetcher/plugins/scraperapi_plugin.py

import os
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from .base import SourcePlugin

class ScraperApiPlugin(SourcePlugin):
    """
    Plugin für scraperapi.com.
    SOURCE_SPECS-Args: URL, item_selector, optional title_selector, link_selector, date_selector.
    """
    def __init__(
        self,
        url: str,
        item_selector: str,
        title_selector: str = None,
        link_selector: str = None,
        date_selector: str = None
    ):
        self.url = url
        self.item_selector = item_selector
        self.title_selector = title_selector or item_selector
        self.link_selector = link_selector or "a"
        self.date_selector = date_selector

    async def fetch(self) -> List[Dict]:
        key = os.getenv("SCRAPERAPI_KEY")
        if not key:
            raise RuntimeError("SCRAPERAPI_KEY nicht gesetzt")

        api_url = (
            f"http://api.scraperapi.com"
            f"?api_key={key}"
            f"&url={self.url}"
            f"&render=true"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=30) as resp:
                html = await resp.text()

        soup = BeautifulSoup(html, "lxml")
        items = []

        for node in soup.select(self.item_selector):
            title_node = node.select_one(self.title_selector)
            title = title_node.get_text(strip=True) if title_node else ""

            link_node = node.select_one(self.link_selector)
            link = link_node.get("href", self.url) if link_node else self.url

            if self.date_selector:
                date_node = node.select_one(self.date_selector)
                try:
                    published = datetime.fromisoformat(date_node.get_text(strip=True))
                except Exception:
                    published = datetime.utcnow()
            else:
                published = datetime.utcnow()

            items.append({
                "title": title,
                "link": link,
                "published": published,
                "source": self.url
            })

        return items
