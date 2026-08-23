from __future__ import annotations

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery"
CACHE_DIR = ARTIFACTS / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    {"id": "fitness", "hashtag": "fitness", "url": "https://www.instagram.com/explore/tags/fitness/"},
    {"id": "beleza", "hashtag": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "hashtag": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]

MAX_PER_SCENARIO = 30
READY_FILE = CACHE_DIR / "ready.flag"


async def main() -> None:
    print("=" * 60)
    print("  BROWSER DISCOVERY — MODO INTERATIVO")
    print("=" * 60)
    print()
    print("1. O browser vai abrir o Instagram.")
    print("2. Faca login manualmente no browser.")
    print("3. Crie o arquivo 'ready.flag' para iniciar coleta:")
    print()
    print("   powershell: New-Item -Path 'artifacts/browser-discovery/cache/ready.flag' -ItemType File")
    print()
    print("   ou aguarde 120 segundos para coleta automatica.")
    print()

    if READY_FILE.exists():
        READY_FILE.unlink()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        print("Abrindo Instagram...")
        try:
            await page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"  Navegacao timeout, continuando...")
        await asyncio.sleep(3)

        print()
        print(">>> FACAA LOGIN NO BROWSER AGORA <<<")
        print()
        print("Aguardando login (max 120s)...")
        print()

        for i in range(120):
            if READY_FILE.exists():
                print("ready.flag detectado!")
                READY_FILE.unlink()
                break
            await asyncio.sleep(1)
            if i % 15 == 0 and i > 0:
                print(f"  Aguardando... ({i}s)")
        else:
            print("Timeout. Tentando coletar...")

        print()
        print("Salvando sessao...")
        state = await context.storage_state()
        state_path = CACHE_DIR / "instagram_session.json"
        state_path.write_text(json.dumps(state), encoding="utf-8")

        all_contents: list[dict] = []

        for scenario in SCENARIOS:
            print()
            print(f"--- Cenario: {scenario['id']} ---")

            try:
                await page.goto(scenario["url"], wait_until="domcontentloaded")
                await asyncio.sleep(3)

                is_auth = await _check_auth(page)
                if is_auth:
                    print("  AUTH_REQUIRED. Pulando.")
                    continue

                print("  Coletando...")
                contents = await _extract_contents(page, MAX_PER_SCENARIO)
                print(f"  {len(contents)} conteudos")

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
        return any(ind in lower for ind in ["log in", "login", "sign up", "sign in", "create account"])
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
