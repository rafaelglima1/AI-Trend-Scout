import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    session = Path("artifacts/browser-discovery/cache/instagram_session.json")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=str(session), viewport={"width":1280,"height":720})
        page = await context.new_page()
        await page.goto("https://www.instagram.com/explore/tags/beleza/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        links = await page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
        print(f"Found {len(links)} links")
        
        for link in links[:5]:
            href = await link.get_attribute("href")
            if href:
                url = f"https://www.instagram.com{href}" if href.startswith("/") else href
                print(f"  {url}")
        
        await browser.close()

asyncio.run(main())
