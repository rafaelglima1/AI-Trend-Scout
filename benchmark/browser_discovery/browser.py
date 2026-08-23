from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from benchmark.browser_discovery.config import BrowserConfig


class BrowserManager:
    def __init__(self, config: BrowserConfig) -> None:
        self.config = config
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> Page:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.config.headless,
        )
        self._context = await self._browser.new_context(
            viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self._page = await self._context.new_page()
        return self._page

    async def stop(self) -> None:
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def navigate(self, url: str) -> tuple[bool, str]:
        try:
            response = await self._page.goto(url, wait_until="domcontentloaded", timeout=self.config.timeout_ms)
            if response and response.status == 200:
                await asyncio.sleep(2)
                return True, ""
            elif response and response.status == 404:
                return False, "PAGE_NOT_FOUND"
            elif response and response.status >= 400:
                return False, f"HTTP_{response.status}"
            else:
                return True, ""
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str:
                return False, "TIMEOUT"
            return False, f"NAVIGATION_FAILURE: {str(e)[:100]}"

    async def check_auth_required(self) -> bool:
        try:
            content = await self._page.content()
            lower = content.lower()
            auth_indicators = [
                "log in", "login", "sign up", "sign in",
                "create account", "enter your", "please log",
                "login_page", "accounts/login",
            ]
            for indicator in auth_indicators:
                if indicator in lower:
                    return True
            return False
        except Exception:
            return False

    async def check_captcha(self) -> bool:
        try:
            content = await self._page.content()
            lower = content.lower()
            captcha_indicators = [
                "captcha", "recaptcha", "verify you are human",
                "security check", "unusual traffic", "blocked",
            ]
            for indicator in captcha_indicators:
                if indicator in lower:
                    return True
            return False
        except Exception:
            return False

    async def save_screenshot(self, path: Path) -> None:
        try:
            await self._page.screenshot(path=str(path), full_page=False)
        except Exception:
            pass
