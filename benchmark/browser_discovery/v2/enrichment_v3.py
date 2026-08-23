from __future__ import annotations

import asyncio
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import Page

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery" / "v3"
RAW = ARTIFACTS / "raw"
NORM = ARTIFACTS / "normalized"
SCREENSHOTS = ARTIFACTS / "screenshots"
for d in [RAW, NORM, SCREENSHOTS]:
    d.mkdir(parents=True, exist_ok=True)

SESSION = ROOT / "artifacts" / "browser-discovery" / "cache" / "instagram_session.json"

SCENARIOS = [
    {"id": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]

MAX_LISTING = 15
MAX_ENRICH = 10
MAX_TOTAL = 20
MAX_SCROLLS = 3


async def run_v3() -> dict:
    from playwright.async_api import async_playwright

    results = {
        "scenarios": [],
        "listing_total": 0,
        "selected_total": 0,
        "attempted_total": 0,
        "successful_total": 0,
        "failed_total": 0,
        "all_enriched": [],
    }

    if not SESSION.exists():
        return {"error": "No session"}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(SESSION),
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        for scenario in SCENARIOS:
            if len(results["all_enriched"]) >= MAX_TOTAL:
                break

            remaining = MAX_TOTAL - len(results["all_enriched"])
            enrich_limit = min(MAX_ENRICH, remaining)

            listing = await _get_listing(page, scenario)
            selected = listing[:MAX_LISTING]
            enriched = await _enrich_posts(page, selected[:enrich_limit], scenario["id"])

            results["scenarios"].append({
                "id": scenario["id"],
                "listing_count": len(listing),
                "selected_count": len(selected),
                "attempted": len(selected[:enrich_limit]),
                "successful": len(enriched),
            })
            results["listing_total"] += len(listing)
            results["selected_total"] += len(selected)
            results["attempted_total"] += len(selected[:enrich_limit])
            results["successful_total"] += len(enriched)
            results["all_enriched"].extend(enriched)

        await browser.close()

    return results


async def _get_listing(page: Page, scenario: dict) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    try:
        await page.goto(scenario["url"], wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        for _ in range(MAX_SCROLLS):
            links = await page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
            for link in links:
                if len(urls) >= MAX_LISTING:
                    break
                try:
                    href = await link.get_attribute("href")
                    if not href or href in seen:
                        continue
                    seen.add(href)
                    urls.append(f"https://www.instagram.com{href}" if href.startswith("/") else href)
                except Exception:
                    continue
            if len(urls) >= MAX_LISTING:
                break
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(1)
    except Exception:
        pass
    return urls


async def _enrich_posts(page: Page, urls: list[str], scenario_id: str) -> list[dict]:
    enriched: list[dict] = []
    for url in urls:
        result = await _extract_post(page, url, scenario_id)
        if result.get("status") == "SUCCESS":
            enriched.append(result)
    return enriched


async def _extract_post(page: Page, url: str, scenario_id: str) -> dict:
    from benchmark.browser_discovery.extraction_v3 import extract_author, extract_comment_count, extract_like_count, classify_media_type

    result: dict[str, Any] = {
        "url": url,
        "scenario": scenario_id,
        "status": "PENDING",
        "content_id": _extract_id(url),
        "author": None,
        "author_id": None,
        "text": None,
        "caption": None,
        "published_at": None,
        "hashtags": [],
        "media_type": "UNKNOWN",
        "is_video": False,
        "is_reel": "/reel/" in url,
        "like_count": None,
        "comment_count": None,
        "view_count": None,
        "audio_reference": None,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "error": None,
    }

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2)

        if "login" in page.url.lower():
            result["status"] = "AUTH_REQUIRED"
            return result

        html = await page.content()

        # Extract from og:description
        og_desc = re.search(r'<meta\s+(?:name|property)="og:description"\s+content="([^"]+)"', html, re.IGNORECASE)
        text = ""
        if og_desc:
            text = og_desc.group(1)
            result["text"] = text[:500]

        # V3: Extract author from text
        result["author"] = extract_author(text)

        # V3: Extract comment count from text
        result["comment_count"] = extract_comment_count(text)

        # V3: Extract like count from text
        result["like_count"] = extract_like_count(text)

        # V3: Classify media type from HTML
        media_type, is_video, is_reel = classify_media_type(html, text, url)
        result["media_type"] = media_type
        result["is_video"] = is_video
        result["is_reel"] = is_reel

        # Extract hashtags from text
        hashtags = re.findall(r"#(\w+)", text)
        result["hashtags"] = list(set(hashtags))

        # Extract published_at
        ts_match = re.search(r'<time\s+datetime="([^"]+)"', html)
        if ts_match:
            result["published_at"] = ts_match.group(1)
        else:
            # Try to extract from text: "March 14, 2026"
            date_match = re.search(r"on\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
            if date_match:
                result["published_at"] = date_match.group(1)

        result["status"] = "SUCCESS"

    except Exception as e:
        result["status"] = "TIMEOUT" if "timeout" in str(e).lower() else "ERROR"
        result["error"] = str(e)[:200]

    return result


def _extract_id(url: str) -> str:
    m = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", url)
    return m.group(2) if m else url.split("/")[-1] if "/" in url else url
