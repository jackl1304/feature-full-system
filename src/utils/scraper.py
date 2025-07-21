import random, asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from typing import List, Dict

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
]

async def human_fetch(url: str, selector: str) -> List[Dict]:
    await asyncio.sleep(random.uniform(1.5, 4.0))
    ua = random.choice(USER_AGENTS)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(user_agent=ua, viewport={"width":1280,"height":800})
        page = await ctx.new_page()
        await page.goto(url)
        await page.wait_for_selector(selector)
        elems = await page.query_selector_all(selector)
        items = []
        for el in elems:
            text = (await el.inner_text()).strip()
            href = await el.get_attribute("href") or url
            items.append({
                "title": text,
                "link": href,
                "published": datetime.utcnow().isoformat(),
                "source": url
            })
        await browser.close()
    return items
