import asyncio
import json
import re
import time
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    session = Path("artifacts/browser-discovery/cache/instagram_session.json")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(session),
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        await page.goto("https://www.instagram.com/explore/tags/beleza/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        links = await page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
        print(f"Listing: {len(links)} links")

        urls = []
        for link in links[:3]:
            href = await link.get_attribute("href")
            if href:
                url = f"https://www.instagram.com{href}" if href.startswith("/") else href
                urls.append(url)

        if urls:
            url = urls[0]
            print(f"Visiting: {url}")
            start = time.monotonic()
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)
            duration = time.monotonic() - start
            print(f"Loaded in {duration:.2f}s")

            current_url = page.url
            print(f"Current URL: {current_url}")

            is_login = "login" in current_url.lower()
            print(f"Login page: {is_login}")

            if not is_login:
                content = await page.content()
                print(f"Content length: {len(content)}")

                author_match = re.search(r'<meta\s+(?:name|property)="(?:og:)?author"\s+content="([^"]+)"', content)
                if author_match:
                    print(f"Author: {author_match.group(1)}")
                else:
                    print("Author: not found in meta")

                title_match = re.search(r'<meta\s+(?:name|property)="og:title"\s+content="([^"]+)"', content)
                if title_match:
                    print(f"Title: {title_match.group(1)[:80]}")

                desc_match = re.search(r'<meta\s+(?:name|property)="og:description"\s+content="([^"]+)"', content)
                if desc_match:
                    print(f"Description: {desc_match.group(1)[:80]}")

        await browser.close()

asyncio.run(main())
