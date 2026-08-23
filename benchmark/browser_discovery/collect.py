from __future__ import annotations

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery"
CACHE_DIR = ARTIFACTS / "cache"
SCREENSHOTS_DIR = ARTIFACTS / "screenshots"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    {"id": "fitness", "hashtag": "fitness", "url": "https://www.instagram.com/explore/tags/fitness/"},
    {"id": "beleza", "hashtag": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "hashtag": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]

MAX_PER_SCENARIO = 30


async def main() -> None:
    print("=" * 60)
    print("  BROWSER DISCOVERY — USANDO SESSAO SALVA")
    print("=" * 60)
    print()

    session_path = CACHE_DIR / "instagram_session.json"
    if not session_path.exists():
        print("Nenhuma sessao salva. Execute o modo interativo primeiro.")
        return

    session_data = json.loads(session_path.read_text(encoding="utf-8"))
    print(f"Sessao carregada: {len(session_data.get('cookies', []))} cookies")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(session_path),
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        print()
        print("Testando acesso ao Instagram...")
        try:
            await page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"  Navegacao: {e}")

        is_auth = await _check_auth(page)
        print(f"  Auth required: {is_auth}")

        if is_auth:
            print()
            print("Sessao invalida. Tentando sem login...")
            await context.close()
            context = await browser.new_context(viewport={"width": 1280, "height": 720})
            page = await context.new_page()

        all_contents: list[dict] = []

        for scenario in SCENARIOS:
            print()
            print(f"--- Cenario: {scenario['id']} ---")
            print(f"URL: {scenario['url']}")

            try:
                await page.goto(scenario["url"], wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)

                await page.screenshot(path=str(SCREENSHOTS_DIR / f"{scenario['id']}.png"))

                is_auth = await _check_auth(page)
                if is_auth:
                    print("  AUTH_REQUIRED")
                    continue

                print("  Coletando...")
                contents = await _extract_contents(page, MAX_PER_SCENARIO)
                print(f"  {len(contents)} conteudos encontrados")

                for c in contents:
                    c["_scenario"] = scenario["id"]
                all_contents.extend(contents)

                raw_path = ARTIFACTS / "raw" / f"scenario_{scenario['id']}.json"
                raw_path.parent.mkdir(parents=True, exist_ok=True)
                raw_path.write_text(json.dumps(contents, indent=2, default=str), encoding="utf-8")

            except Exception as e:
                print(f"  Erro: {e}")

        print()
        print("=" * 60)
        print(f"Total: {len(all_contents)} conteudos")

        if all_contents:
            all_path = CACHE_DIR / "all_contents.json"
            all_path.write_text(json.dumps(all_contents, indent=2, default=str), encoding="utf-8")
            print(f"Cache: {all_path}")

        await browser.close()

    print("Concluido.")


async def _check_auth(page) -> bool:
    try:
        content = await page.content()
        lower = content.lower()
        indicators = ["log in", "login", "sign up", "sign in", "create account"]
        return any(ind in lower for ind in indicators)
    except Exception:
        return False


async def _extract_contents(page, max_contents: int) -> list[dict]:
    import re
    contents: list[dict] = []
    seen_urls: set[str] = set()

    links = await page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')

    for link in links:
        if len(contents) >= max_contents:
            break
        try:
            href = await link.get_attribute("href")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)
            url = f"https://www.instagram.com{href}" if href.startswith("/") else href
            media_type = "reel" if "/reel/" in href else "unknown"
            content_id = ""
            match = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", href)
            if match:
                content_id = match.group(2)
            inner_text = await link.inner_text()
            text = inner_text.strip()[:500] if inner_text else ""
            contents.append({
                "id": content_id, "url": url, "media_type": media_type,
                "text": text, "collected_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception:
            continue

    if not contents:
        all_links = await page.query_selector_all("a[href]")
        for link in all_links:
            if len(contents) >= max_contents:
                break
            try:
                href = await link.get_attribute("href")
                if not href:
                    continue
                if "/p/" in href or "/reel/" in href:
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    url = f"https://www.instagram.com{href}" if href.startswith("/") else href
                    media_type = "reel" if "/reel/" in href else "unknown"
                    content_id = ""
                    match = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", href)
                    if match:
                        content_id = match.group(2)
                    contents.append({
                        "id": content_id, "url": url, "media_type": media_type,
                        "text": "", "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception:
                continue

    return contents


if __name__ == "__main__":
    asyncio.run(main())
