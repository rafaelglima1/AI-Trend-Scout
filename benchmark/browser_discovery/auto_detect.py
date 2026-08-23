from __future__ import annotations

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery"
CACHE_DIR = ARTIFACTS / "cache"
RAW_DIR = ARTIFACTS / "raw"
SCREENSHOTS_DIR = ARTIFACTS / "screenshots"
for d in [CACHE_DIR, RAW_DIR, SCREENSHOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    {"id": "fitness", "url": "https://www.instagram.com/explore/tags/fitness/"},
    {"id": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]
MAX_PER_SCENARIO = 30


async def main() -> None:
    print("Browser vai abrir. Faca login.")
    print("Assim que estiver logado, o script detecta sozinho.")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        await page.goto("https://www.instagram.com/", wait_until="load", timeout=60000)
        await asyncio.sleep(2)

        print("Aguardando login...")
        logged_in = False
        for i in range(300):
            await asyncio.sleep(2)
            try:
                url = page.url
                if "/accounts/login" not in url and "instagram.com" in url:
                    content = await page.content()
                    if "log into instagram" not in content.lower() and "password" not in content.lower():
                        logged_in = True
                        print(f"Login detectado em {i}s!")
                        break
            except Exception:
                pass
            if i % 15 == 0 and i > 0:
                print(f"  {i}s...")

        if not logged_in:
            print("Login nao detectado.")
            await browser.close()
            return

        state = await context.storage_state()
        session_path = CACHE_DIR / "instagram_session.json"
        session_path.write_text(json.dumps(state), encoding="utf-8")
        print(f"Sessao salva: {len(state.get('cookies',[]))} cookies")

        all_contents: list[dict] = []

        for scenario in SCENARIOS:
            print(f"\n--- {scenario['id']} ---")
            try:
                await page.goto(scenario["url"], wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)
                await page.screenshot(path=str(SCREENSHOTS_DIR / f"final_{scenario['id']}.png"))

                login_check = await _is_login_page(page)
                if login_check:
                    print("  Login necessario. Pulando.")
                    continue

                contents = await _extract(page, MAX_PER_SCENARIO)
                print(f"  {len(contents)} conteudos")
                for c in contents:
                    c["_scenario"] = scenario["id"]
                all_contents.extend(contents)

                path = RAW_DIR / f"scenario_{scenario['id']}.json"
                path.write_text(json.dumps(contents, indent=2, default=str), encoding="utf-8")
            except Exception as e:
                print(f"  Erro: {e}")

        print(f"\nTotal: {len(all_contents)} conteudos")
        if all_contents:
            p = CACHE_DIR / "all_contents.json"
            p.write_text(json.dumps(all_contents, indent=2, default=str), encoding="utf-8")
            print(f"Cache: {p}")

        await browser.close()
    print("Concluido.")


async def _is_login_page(page) -> bool:
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
