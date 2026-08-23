from __future__ import annotations

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery"
CACHE = ARTIFACTS / "cache"
RAW = ARTIFACTS / "raw"
RAW.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    {"id": "fitness", "url": "https://www.instagram.com/explore/tags/fitness/"},
    {"id": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]


async def main() -> None:
    session = CACHE / "instagram_session.json"
    print(f"Sessao: {session}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(session),
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        # Test login
        print("Testando login...")
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        url = page.url
        print(f"URL atual: {url}")

        is_login = await _is_login(page)
        print(f"Login page: {is_login}")

        if is_login:
            print("Sessao invalida.")
            await browser.close()
            return

        print("Login OK!")
        print()

        all_contents = []

        for sc in SCENARIOS:
            print(f"--- {sc['id']} ---")
            try:
                await page.goto(sc["url"], wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)

                current_url = page.url
                print(f"  URL: {current_url}")

                if "login" in current_url.lower():
                    print("  Redirect para login. Pulando.")
                    continue

                contents = await _extract(page, 30)
                print(f"  {len(contents)} conteudos")

                for c in contents:
                    c["_scenario"] = sc["id"]
                all_contents.extend(contents)

                path = RAW / f"scenario_{sc['id']}.json"
                path.write_text(json.dumps(contents, indent=2, default=str), encoding="utf-8")

            except Exception as e:
                print(f"  Erro: {e}")

        print()
        print(f"Total: {len(all_contents)} conteudos")

        if all_contents:
            p = CACHE / "all_contents.json"
            p.write_text(json.dumps(all_contents, indent=2, default=str), encoding="utf-8")
            print(f"Salvo: {p}")

        await browser.close()


async def _is_login(page) -> bool:
    try:
        if "login" in page.url.lower():
            return True
        c = await page.content()
        return "log into instagram" in c.lower()
    except Exception:
        return False


async def _extract(page, limit: int) -> list[dict]:
    import re
    contents, seen = [], set()
    for sel in ['a[href*="/p/"]', 'a[href*="/reel/"]']:
        for link in await page.query_selector_all(sel):
            if len(contents) >= limit:
                break
            try:
                href = await link.get_attribute("href")
                if not href or href in seen:
                    continue
                seen.add(href)
                url = f"https://www.instagram.com{href}" if href.startswith("/") else href
                media = "reel" if "/reel/" in href else "unknown"
                cid = ""
                m = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", href)
                if m:
                    cid = m.group(2)
                text = ""
                try:
                    text = (await link.inner_text()).strip()[:500]
                except Exception:
                    pass
                contents.append({"id": cid, "url": url, "media_type": media,
                                 "text": text, "collected_at": datetime.now(timezone.utc).isoformat()})
            except Exception:
                continue
    return contents


if __name__ == "__main__":
    asyncio.run(main())
