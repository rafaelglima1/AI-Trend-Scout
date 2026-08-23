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
CACHE_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    {"id": "fitness", "hashtag": "fitness", "url": "https://www.instagram.com/explore/tags/fitness/"},
    {"id": "beleza", "hashtag": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "hashtag": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]

MAX_PER_SCENARIO = 30
READY_FILE = CACHE_DIR / "ready.flag"


async def main() -> None:
    print("=" * 60)
    print("  STEP 1: LOGIN")
    print("=" * 60)
    print()
    print("Browser vai abrir. Faca login no Instagram.")
    print("Depois de logado, execute em OUTRO terminal:")
    print()
    print("  echo done > artifacts\\browser-discovery\\cache\\ready.flag")
    print()

    if READY_FILE.exists():
        READY_FILE.unlink()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        await page.goto("https://www.instagram.com/", wait_until="load", timeout=60000)
        await asyncio.sleep(2)

        print("Browser aberto. Aguardando login...")

        for i in range(300):
            if READY_FILE.exists():
                READY_FILE.unlink()
                break
            await asyncio.sleep(1)
            if i % 30 == 0 and i > 0:
                print(f"  {i}s...")
        else:
            print("Timeout.")
            await browser.close()
            return

        print()
        print("Login detectado! Salvando sessao...")
        state = await context.storage_state()
        session_path = CACHE_DIR / "instagram_session.json"
        session_path.write_text(json.dumps(state), encoding="utf-8")
        print(f"Sessao salva: {len(state.get('cookies', []))} cookies")

        print()
        print("=" * 60)
        print("  STEP 2: COLETA")
        print("=" * 60)

        all_contents: list[dict] = []

        for scenario in SCENARIOS:
            print()
            print(f"--- {scenario['id']} ---")

            try:
                await page.goto(scenario["url"], wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)

                await page.screenshot(path=str(SCREENSHOTS_DIR / f"post_login_{scenario['id']}.png"))

                login_page = await _check_login_page(page)
                if login_page:
                    print("  Login necessario. Pulando.")
                    continue

                print("  Coletando...")
                contents = await _extract(page, MAX_PER_SCENARIO)
                print(f"  {len(contents)} conteudos")

                for c in contents:
                    c["_scenario"] = scenario["id"]
                all_contents.extend(contents)

                path = RAW_DIR / f"scenario_{scenario['id']}.json"
                path.write_text(json.dumps(contents, indent=2, default=str), encoding="utf-8")

            except Exception as e:
                print(f"  Erro: {e}")

        print()
        print(f"Total: {len(all_contents)} conteudos")

        if all_contents:
            cache_path = CACHE_DIR / "all_contents.json"
            cache_path.write_text(json.dumps(all_contents, indent=2, default=str), encoding="utf-8")
            print(f"Cache: {cache_path}")

        await browser.close()

    print("Concluido.")


async def _check_login_page(page) -> bool:
    try:
        url = page.url
        if "login" in url.lower():
            return True
        content = await page.content()
        lower = content.lower()
        return "log into instagram" in lower or ("log in" in lower and "password" in lower)
    except Exception:
        return False


async def _extract(page, max_contents: int) -> list[dict]:
    import re
    contents: list[dict] = []
    seen: set[str] = set()

    selectors = [
        'a[href*="/p/"]',
        'a[href*="/reel/"]',
        'a[href*="/reels/"]',
    ]

    for sel in selectors:
        links = await page.query_selector_all(sel)
        for link in links:
            if len(contents) >= max_contents:
                break
            try:
                href = await link.get_attribute("href")
                if not href or href in seen:
                    continue
                seen.add(href)

                url_full = f"https://www.instagram.com{href}" if href.startswith("/") else href
                media_type = "reel" if "/reel/" in href else "unknown"
                cid = ""
                m = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", href)
                if m:
                    cid = m.group(2)

                text = ""
                try:
                    text = (await link.inner_text()).strip()[:500]
                except Exception:
                    pass

                contents.append({
                    "id": cid, "url": url_full, "media_type": media_type,
                    "text": text, "collected_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception:
                continue

    return contents


if __name__ == "__main__":
    asyncio.run(main())
