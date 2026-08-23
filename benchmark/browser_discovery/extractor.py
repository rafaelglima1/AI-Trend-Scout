from __future__ import annotations

import re
import json
from datetime import datetime, timezone
from typing import Any

from playwright.async_api import Page


async def extract_contents(page: Page, max_contents: int) -> list[dict]:
    contents: list[dict] = []

    links = await page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    seen_urls: set[str] = set()

    for link in links:
        if len(contents) >= max_contents:
            break

        try:
            href = await link.get_attribute("href")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)

            url = f"https://www.instagram.com{href}" if href.startswith("/") else href
            media_type = _detect_media_type(href)

            inner_text = await link.inner_text()
            img = await link.query_selector("img")
            img_src = await img.get_attribute("src") if img else None

            content = {
                "id": _extract_id_from_url(href),
                "url": url,
                "media_type": media_type,
                "text": inner_text.strip() if inner_text else "",
                "image_url": img_src,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }

            contents.append(content)

        except Exception:
            continue

    post_links = await page.query_selector_all('article a[href*="/p/"], div a[href*="/p/"]')
    for link in post_links:
        if len(contents) >= max_contents:
            break
        try:
            href = await link.get_attribute("href")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)
            url = f"https://www.instagram.com{href}" if href.startswith("/") else href
            content = {
                "id": _extract_id_from_url(href),
                "url": url,
                "media_type": "unknown",
                "text": "",
                "image_url": None,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }
            contents.append(content)
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
                    media_type = _detect_media_type(href)
                    content = {
                        "id": _extract_id_from_url(href),
                        "url": url,
                        "media_type": media_type,
                        "text": "",
                        "image_url": None,
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    }
                    contents.append(content)
            except Exception:
                continue

    return contents


async def extract_post_details(page: Page, url: str) -> dict:
    details: dict[str, Any] = {}

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(1)

        json_ld = await page.query_selector('script[type="application/ld+json"]')
        if json_ld:
            try:
                ld_text = await json_ld.inner_text()
                ld_data = json.loads(ld_text)
                if isinstance(ld_data, dict):
                    details["author"] = ld_data.get("author", {}).get("name")
                    details["published_at"] = ld_data.get("datePublished")
                    details["text"] = ld_data.get("articleBody", "")[:500]
                    details["media_type"] = ld_data.get("articleSection", "unknown")
            except Exception:
                pass

        if "author" not in details:
            meta_author = await page.query_selector('meta[name="author"]')
            if meta_author:
                details["author"] = await meta_author.get_attribute("content")

        if "text" not in details:
            desc = await page.query_selector('meta[property="og:description"]')
            if desc:
                details["text"] = (await desc.get_attribute("content", ""))[:500]

        if "media_type" not in details:
            og_type = await page.query_selector('meta[property="og:type"]')
            if og_type:
                og_val = await og_type.get_attribute("content", "")
                if "video" in og_val:
                    details["media_type"] = "video"
                else:
                    details["media_type"] = "image"

        likes = await page.query_selector('a[href*="liked_by"] span, section span')
        if likes:
            try:
                likes_text = await likes.inner_text()
                likes_text = likes_text.replace(",", "").replace(".", "").strip()
                if likes_text.isdigit():
                    details["like_count"] = int(likes_text)
            except Exception:
                pass

        time_el = await page.query_selector("time[datetime]")
        if time_el and "published_at" not in details:
            details["published_at"] = await time_el.get_attribute("datetime")

    except Exception:
        pass

    return details


def _extract_id_from_url(href: str) -> str:
    match = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", href)
    if match:
        return match.group(2)
    return href.split("/")[-1] if "/" in href else href


def _detect_media_type(href: str) -> str:
    if "/reel/" in href:
        return "reel"
    return "unknown"


import asyncio
