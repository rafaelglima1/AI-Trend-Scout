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
ARTIFACTS = ROOT / "artifacts" / "browser-discovery" / "v2"
SCREENSHOTS = ARTIFACTS / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    {"id": "beleza", "hashtag": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "hashtag": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]

MAX_LISTING = 15
MAX_ENRICH = 10
MAX_TOTAL = 20
MAX_SCROLLS = 3


def extract_author(text: str) -> str | None:
    if not text:
        return None

    patterns = [
        r"-\s*([a-zA-Z0-9_.]+)\s+on\s+",
        r"^([a-zA-Z0-9_.]+)\s+on\s+",
        r"^([a-zA-Z0-9_.]+)\s+-\s+",
        r"-\s*([a-zA-Z0-9_.]+)\s+-\s+",
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            author = m.group(1)
            if not author or len(author) < 2:
                continue
            if author.lower() in ("instagram", "whatsapp", "meta", "and"):
                continue
            return author

    return None


def extract_comment_count(text: str) -> int | None:
    if not text:
        return None

    patterns = [
        r"([\d,\.]+)\s*K?\s*comments?",
        r"([\d,\.]+)\s*K?\s*comment",
        r"comments?\s*:?\s*([\d,\.]+)\s*K?",
        r"([\d,\.]+)\s*K?\s*coms?",
    ]

    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            raw = m.group(1)
            try:
                if "K" in raw.upper():
                    return int(float(raw.upper().replace("K", "")) * 1000)
                return int(raw.replace(",", "").replace(".", ""))
            except ValueError:
                continue

    return None


def extract_like_count(text: str) -> int | None:
    if not text:
        return None

    patterns = [
        r"([\d,\.]+)\s*K?\s*likes?",
        r"([\d,\.]+)\s*K?\s*like",
        r"likes?\s*:?\s*([\d,\.]+)\s*K?",
    ]

    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            raw = m.group(1)
            try:
                if "K" in raw.upper():
                    return int(float(raw.upper().replace("K", "")) * 1000)
                return int(raw.replace(",", "").replace(".", ""))
            except ValueError:
                continue

    return None


def classify_media_type(html: str, text: str, url: str) -> tuple[str, bool, bool]:
    is_video = False
    is_reel = "/reel/" in url

    if is_reel:
        return "REEL", True, True

    html_lower = html.lower()

    video_indicators = [
        'og:type="video', '"og:type":"video', 'property="og:video"',
        'og:video:url', 'og:video:type', 'og:video:width', 'og:video:height',
        'twitter:player', 'twitter:player:width', 'twitter:player:height',
        '"@type":"VideoObject"', 'videoobject', '"content_type":"video"',
        '"media_type":"video"', '"type":"video"', 'video/mp4',
    ]
    for indicator in video_indicators:
        if indicator in html_lower:
            is_video = True
            break

    carousel_indicators = [
        '"@type":"CarouselMedia"', 'carouselmedia', 'carousel media',
        '"@type":"ImageGallery"', 'imagegallery', 'image gallery',
        'sidecar', 'multi_image', 'multiple_images', 'carousel',
    ]
    is_carousel = any(indicator in html_lower for indicator in carousel_indicators)

    if is_carousel:
        return "CAROUSEL", False, False

    if is_video:
        return "VIDEO", True, False

    image_indicators = [
        'og:image', 'og:image:url', 'og:image:type', 'og:image:width', 'og:image:height',
        'twitter:image', 'twitter:image:src', 'thumbnail_url',
        '"@type":"ImageObject"', 'imageobject', 'image_object',
        '"content_type":"image"', '"media_type":"image"', 'image/jpeg',
        '"type":"image"', 'image/',
    ]
    is_image = any(indicator in html_lower for indicator in image_indicators)

    if is_image:
        return "IMAGE", False, False

    return "UNKNOWN", False, False


async def run_v2() -> dict:
    session_path = ROOT / "artifacts" / "browser-discovery" / "cache" / "instagram_session.json"
    if not session_path.exists():
        return {"error": "No session found"}

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

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(session_path),
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        for scenario in SCENARIOS:
            if len(results["all_enriched"]) >= MAX_TOTAL:
                break

            print(f"\n--- {scenario['id']} ---")
            remaining = MAX_TOTAL - len(results["all_enriched"])
            enrich_limit = min(MAX_ENRICH, remaining)

            listing = await _get_listing(page, scenario)
            print(f"  Listing: {len(listing)} URLs")

            selected = listing[:MAX_LISTING]
            print(f"  Selected: {len(selected)}")

            enriched = await _enrich_posts(page, selected[:enrich_limit], scenario["id"])
            print(f"  Enriched: {len(enriched)}")

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
                    url = f"https://www.instagram.com{href}" if href.startswith("/") else href
                    urls.append(url)
                except Exception:
                    continue
            if len(urls) >= MAX_LISTING:
                break
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(1)
    except Exception as e:
        print(f"  Listing error: {e}")

    return urls


async def _enrich_posts(page: Page, urls: list[str], scenario_id: str) -> list[dict]:
    enriched: list[dict] = []

    for idx, url in enumerate(urls):
        print(f"    [{idx+1}/{len(urls)}] {url[-30:]}")
        start = time.monotonic()
        result = await _extract_post(page, url, scenario_id)
        duration = time.monotonic() - start

        result["extraction_duration_seconds"] = round(duration, 2)

        if result.get("status") == "SUCCESS":
            enriched.append(result)
        else:
            print(f"      {result.get('status')}: {result.get('error', '')[:50]}")

    return enriched


async def _extract_post(page: Page, url: str, scenario_id: str) -> dict:
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
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2)

        if resp and resp.status == 404:
            result["status"] = "PAGE_NOT_FOUND"
            return result

        is_login = await _check_login(page)
        if is_login:
            result["status"] = "AUTH_REQUIRED"
            return result

        content = await page.content()

        _extract_meta(result, content)
        _extract_og(result, content)
        _extract_jsonld(result, content)
        await _extract_dom(result, page)

        if result["is_reel"]:
            result["media_type"] = "REEL"
        elif result["is_video"]:
            result["media_type"] = "VIDEO"

        result["status"] = "SUCCESS"

    except Exception as e:
        error_str = str(e).lower()
        if "timeout" in error_str:
            result["status"] = "TIMEOUT"
        else:
            result["status"] = "EXTRACTION_FAILURE"
        result["error"] = str(e)[:200]

        try:
            ss_path = SCREENSHOTS / f"{scenario_id}_{result['content_id']}_error.png"
            await page.screenshot(path=str(ss_path))
        except Exception:
            pass

    return result


def _extract_meta(result: dict, html: str) -> None:
    patterns = {
        "author": r'<meta\s+(?:name|property)="(?:og:)?author"\s+content="([^"]+)"',
        "published_at": r'<meta\s+(?:name|property)="(?:article:published_time|og:updated_time)"\s+content="([^"]+)"',
        "text": r'<meta\s+(?:name|property)="og:description"\s+content="([^"]+)"',
    }
    for field, pattern in patterns.items():
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            result[field] = m.group(1)[:500]


def _extract_og(result: dict, html: str) -> None:
    m = re.search(r'<meta\s+property="og:type"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m:
        og_type = m.group(1).lower()
        if "video" in og_type:
            result["is_video"] = True

    m = re.search(r'<meta\s+(?:name|property)="og:title"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m and not result.get("text"):
        result["text"] = m.group(1)[:500]


def _extract_jsonld(result: dict, html: str) -> None:
    m = re.search(r'<script\s+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m:
        return
    try:
        data = json.loads(m.group(1))
        if isinstance(data, dict):
            if "author" in data:
                author = data["author"]
                if isinstance(author, dict):
                    result["author"] = author.get("name")
                elif isinstance(author, str):
                    result["author"] = author
            if "datePublished" in data:
                result["published_at"] = data["datePublished"]
            if "articleBody" in data:
                result["text"] = data["articleBody"][:500]
            if "interactionStatistic" in data:
                for stat in data["interactionStatistic"]:
                    itype = stat.get("interactionType", "")
                    count = stat.get("userInteractionCount")
                    if "comment" in itype:
                        result["comment_count"] = count
                    elif "like" in itype or "heart" in itype:
                        result["like_count"] = count
                    elif "view" in itype or "watch" in itype:
                        result["view_count"] = count
    except Exception:
        pass


async def _extract_dom(result: dict, page: Page) -> None:
    try:
        author_el = await page.query_selector('a[href*="/"] span, header a[href*="/"]')
        if author_el and not result.get("author"):
            text = await author_el.inner_text()
            if text and len(text) < 50:
                result["author"] = text.strip()

        time_el = await page.query_selector("time[datetime]")
        if time_el and not result.get("published_at"):
            result["published_at"] = await time_el.get_attribute("datetime")

        if not result.get("text"):
            desc_el = await page.query_selector('meta[property="og:description"]')
            if desc_el:
                result["text"] = (await desc_el.get_attribute("content", ""))[:500]

        all_text = await page.inner_text("body")
        hashtags = re.findall(r"#(\w+)", all_text)
        if hashtags:
            result["hashtags"] = list(set(hashtags))

        if result["like_count"] is None:
            like_match = re.search(r"([\d,\.]+)\s*(?:likes?|curtidas?)", all_text, re.IGNORECASE)
            if like_match:
                try:
                    result["like_count"] = int(like_match.group(1).replace(",", "").replace(".", ""))
                except Exception:
                    pass

        if result["comment_count"] is None:
            comment_match = re.search(r"([\d,\.]+)\s*(?:comments?|coment[áa]rios?)", all_text, re.IGNORECASE)
            if comment_match:
                try:
                    result["comment_count"] = int(comment_match.group(1).replace(",", "").replace(".", ""))
                except Exception:
                    pass

        if result["view_count"] is None:
            view_match = re.search(r"([\d,\.]+)\s*(?:views?|views?|visualiza[çc][õo]es?)", all_text, re.IGNORECASE)
            if view_match:
                try:
                    result["view_count"] = int(view_match.group(1).replace(",", "").replace(".", ""))
                except Exception:
                    pass

        if not result.get("author"):
            url_author = re.search(r"instagram\.com/([^/]+)/", result.get("url", ""))
            if url_author:
                username = url_author.group(1)
                if username not in ("p", "reel", "explore", "accounts", "direct"):
                    result["author"] = username

    except Exception:
        pass


async def _check_login(page: Page) -> bool:
    try:
        if "login" in page.url.lower():
            return True
        content = await page.content()
        return "log into instagram" in content.lower()
    except Exception:
        return False


def _extract_id(url: str) -> str:
    m = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", url)
    if m:
        return m.group(2)
    return url.split("/")[-1] if "/" in url else url
