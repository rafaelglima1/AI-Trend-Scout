from __future__ import annotations

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = ROOT / "artifacts" / "browser-discovery" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)


async def main() -> None:
    print("1. Browser vai abrir.")
    print("2. Faca login no Instagram.")
    print("3. Depois de logado, pressione CTRL+C neste terminal.")
    print("4. A sessao sera salva automaticamente.")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        await page.goto("https://www.instagram.com/", wait_until="load", timeout=60000)

        print("Browser aberto. Faca login e depois CTRL+C...")
        print()

        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass

        print()
        print("Salvando sessao...")
        state = await context.storage_state()
        path = CACHE / "instagram_session.json"
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        print(f"Salvo: {len(state.get('cookies', []))} cookies")

        cookies = state.get("cookies", [])
        auth_cookies = [c for c in cookies if c.get("name") in ("sessionid", "ds_user_id", "csrftoken")]
        print(f"Cookies de auth: {len(auth_cookies)}")
        for c in auth_cookies:
            print(f"  {c['name']}: {c.get('value', '')[:20]}...")

        await browser.close()

    print("Sessao salva. Agora execute a coleta.")


if __name__ == "__main__":
    asyncio.run(main())
