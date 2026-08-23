from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright, Page

WORKSPACE = Path(r"C:\Users\rafael.dacosta\source\repos\AI Trend Scout")
ARTIFACTS = WORKSPACE / "artifacts" / "browser-discovery" / "v3"
RAW = ARTIFACTS / "raw"
NORM = ARTIFACTS / "normalized"
SCREENSHOTS = ARTIFACTS / "screenshots"
SESSION = WORKSPACE / "artifacts" / "browser-discovery" / "cache" / "instagram_session.json"

for d in [RAW, NORM, SCREENSHOTS]:
    d.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    {"id": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]

MAX_LISTING = 15
MAX_ENRICH = 10
MAX_TOTAL = 20
MAX_SCROLLS = 3


def extract_author(text: str) -> str | None:
    if not text:
        return None
    m = re.search(r"-\s*([a-zA-Z0-9_.]+)\s+on\s+", text)
    if m:
        return m.group(1)
    m = re.search(r"^([a-zA-Z0-9_.]+)\s+on\s+", text)
    if m:
        return m.group(1)
    return None


def extract_comment_count(text: str) -> tuple[int | None, str | None, str | None]:
    if not text:
        return None, None, None
    m = re.search(r"([\d,\.]+)\s*([KMBkmb]?)\s*comments?", text, re.IGNORECASE)
    if not m:
        return None, None, None
    raw_num = m.group(1)
    suffix = m.group(2).upper() if m.group(2) else ""
    raw_match = m.group(0)
    try:
        num = float(raw_num.replace(",", ""))
        if suffix == "K":
            value = int(num * 1000)
        elif suffix == "M":
            value = int(num * 1_000_000)
        elif suffix == "B":
            value = int(num * 1_000_000_000)
        else:
            value = int(num)
        return value, raw_match, "TEXT_OG"
    except ValueError:
        return None, None, None


def extract_like_count(text: str) -> tuple[int | None, str | None, str | None]:
    if not text:
        return None, None, None
    m = re.search(r"([\d,\.]+)\s*([KMBkmb]?)\s*likes?", text, re.IGNORECASE)
    if not m:
        return None, None, None
    raw_num = m.group(1)
    suffix = m.group(2).upper() if m.group(2) else ""
    raw_match = m.group(0)
    try:
        num = float(raw_num.replace(",", ""))
        if suffix == "K":
            value = int(num * 1000)
        elif suffix == "M":
            value = int(num * 1_000_000)
        elif suffix == "B":
            value = int(num * 1_000_000_000)
        else:
            value = int(num)
        return value, raw_match, "TEXT_OG"
    except ValueError:
        return None, None, None


def classify_media_type(html: str, text: str, url: str) -> tuple[str, bool, bool]:
    is_video = False
    is_reel = "/reel/" in url

    if is_reel:
        return "REEL", True, True

    video_indicators = ['og:type="video', '"og:type":"video', 'property="og:video"', "VideoObject", '"@type":"VideoObject"']
    is_video = any(ind.lower() in html.lower() for ind in video_indicators)

    carousel_indicators = ['"@type":"CarouselMedia"', 'carousel_media', '"@type":"ImageGallery"', "sidecar"]
    is_carousel = any(ind.lower() in html.lower() for ind in carousel_indicators)

    if is_carousel:
        return "CAROUSEL", False, False
    if is_video:
        return "VIDEO", True, False

    image_indicators = ['og:image', '"og:image"']
    if any(ind.lower() in html.lower() for ind in image_indicators):
        return "IMAGE", False, False

    return "UNKNOWN", False, False


def _extract_id(url: str) -> str:
    m = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", url)
    return m.group(2) if m else url.split("/")[-1]


async def _get_listing(page: Page, scenario: dict) -> list[str]:
    urls, seen = [], set()
    try:
        await page.goto(scenario["url"], wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        for _ in range(MAX_SCROLLS):
            for link in await page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]'):
                if len(urls) >= MAX_LISTING:
                    break
                href = await link.get_attribute("href")
                if href and href not in seen:
                    seen.add(href)
                    urls.append(f"https://www.instagram.com{href}" if href.startswith("/") else href)
            if len(urls) >= MAX_LISTING:
                break
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(1)
    except Exception:
        pass
    return urls


async def _extract_post(page: Page, url: str, scenario_id: str) -> dict:
    result = {
        "url": url, "scenario": scenario_id, "status": "PENDING",
        "content_id": _extract_id(url), "author": None, "author_id": None,
        "text": None, "published_at": None, "hashtags": [],
        "media_type": "UNKNOWN", "is_video": False, "is_reel": "/reel/" in url,
        "like_count": None, "like_raw": None, "like_source": None,
        "comment_count": None, "comment_raw": None, "comment_source": None,
        "view_count": None, "audio_reference": None, "collected_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2)
        if "login" in page.url.lower():
            result["status"] = "AUTH_REQUIRED"
            return result

        html = await page.content()

        og = re.search(r'<meta\s+(?:name|property)="og:description"\s+content="([^"]+)"', html, re.IGNORECASE)
        text = og.group(1) if og else ""
        result["text"] = text[:500] if text else None

        result["author"] = extract_author(text)
        
        like_val, like_raw, like_src = extract_like_count(text)
        result["like_count"] = like_val
        result["like_raw"] = like_raw
        result["like_source"] = like_src
        
        comment_val, comment_raw, comment_src = extract_comment_count(text)
        result["comment_count"] = comment_val
        result["comment_raw"] = comment_raw
        result["comment_source"] = comment_src

        media, is_vid, is_reel = classify_media_type(html, text, url)
        result["media_type"] = media
        result["is_video"] = is_vid
        result["is_reel"] = is_reel

        result["hashtags"] = list(set(re.findall(r"#(\w+)", text)))

        ts = re.search(r'<time\s+datetime="([^"]+)"', html)
        if ts:
            result["published_at"] = ts.group(1)
        else:
            dm = re.search(r"on\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
            if dm:
                result["published_at"] = dm.group(1)

        result["status"] = "SUCCESS"
    except Exception as e:
        result["status"] = "TIMEOUT" if "timeout" in str(e).lower() else "ERROR"
        result["error"] = str(e)[:200]
    return result


async def main() -> None:
    print("=" * 60)
    print("  BROWSER DISCOVERY POC V3 — METADATA CLOSURE")
    print("=" * 60)
    print()

    if not SESSION.exists():
        print("No session found.")
        return

    all_enriched = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(SESSION),
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        for scenario in SCENARIOS:
            if len(all_enriched) >= MAX_TOTAL:
                break
            remaining = MAX_TOTAL - len(all_enriched)
            limit = min(MAX_ENRICH, remaining)

            print(f"--- {scenario['id']} ---")
            listing = await _get_listing(page, scenario)
            print(f"  Listing: {len(listing)}")

            selected = listing[:MAX_LISTING]
            for url in selected[:limit]:
                post = await _extract_post(page, url, scenario["id"])
                if post["status"] == "SUCCESS":
                    all_enriched.append(post)

            print(f"  Enriched: {len([p for p in all_enriched if p['scenario'] == scenario['id']])}")

        await browser.close()

    # Save artifacts
    for sc in SCENARIOS:
        posts = [p for p in all_enriched if p["scenario"] == sc["id"]]
        RAW / f"{sc['id']}.json"
        (RAW / f"{sc['id']}.json").write_text(json.dumps(posts, indent=2, default=str), encoding="utf-8")
        (NORM / f"{sc['id']}.json").write_text(json.dumps([_normalize(p) for p in posts], indent=2, default=str), encoding="utf-8")

    n = max(len(all_enriched), 1)
    has_author = sum(1 for p in all_enriched if p.get("author"))
    has_text = sum(1 for p in all_enriched if p.get("text"))
    has_hashtags = sum(1 for p in all_enriched if p.get("hashtags"))
    has_timestamp = sum(1 for p in all_enriched if p.get("published_at"))
    has_media = sum(1 for p in all_enriched if p.get("media_type") not in ("UNKNOWN", None))
    has_likes = sum(1 for p in all_enriched if p.get("like_count") is not None)
    has_comments = sum(1 for p in all_enriched if p.get("comment_count") is not None)
    has_views = sum(1 for p in all_enriched if p.get("view_count") is not None)
    has_image = sum(1 for p in all_enriched if p.get("media_type") == "IMAGE")
    has_video = sum(1 for p in all_enriched if p.get("is_video"))
    has_reel = sum(1 for p in all_enriched if p.get("is_reel"))

    core = sum(
        (1 if p.get("author") else 0) +
        (1 if p.get("text") else 0) +
        (1 if p.get("hashtags") else 0) +
        (1 if p.get("published_at") else 0) +
        (1 if p.get("media_type") != "UNKNOWN" else 0)
        for p in all_enriched
    ) / (n * 5)

    rich = sum(
        (1 if p.get("author") else 0) +
        (1 if p.get("text") else 0) +
        (1 if p.get("hashtags") else 0) +
        (1 if p.get("published_at") else 0) +
        (1 if p.get("media_type") != "UNKNOWN" else 0) +
        (1 if p.get("like_count") is not None else 0) +
        (1 if p.get("comment_count") is not None else 0) +
        (1 if p.get("view_count") is not None else 0)
        for p in all_enriched
    ) / (n * 8)

    closure = sum(
        (1 if p.get("author") else 0) +
        (1 if p.get("media_type") != "UNKNOWN" else 0) +
        (1 if p.get("comment_count") is not None else 0)
        for p in all_enriched
    ) / (n * 3)

    print()
    print("=" * 60)
    print(f"Total enriched: {n}")
    print(f"Author: {has_author}/{n} ({has_author/n:.0%})")
    print(f"Text: {has_text}/{n} ({has_text/n:.0%})")
    print(f"Hashtags: {has_hashtags}/{n} ({has_hashtags/n:.0%})")
    print(f"Timestamp: {has_timestamp}/{n} ({has_timestamp/n:.0%})")
    print(f"Media type: {has_media}/{n} ({has_media/n:.0%})")
    print(f"  Image: {has_image}/{n} ({has_image/n:.0%})")
    print(f"  Video: {has_video}/{n} ({has_video/n:.0%})")
    print(f"  Reel: {has_reel}/{n} ({has_reel/n:.0%})")
    print(f"Likes: {has_likes}/{n} ({has_likes/n:.0%})")
    print(f"Comments: {has_comments}/{n} ({has_comments/n:.0%})")
    print(f"Views: {has_views}/{n} ({has_views/n:.0%})")
    print()
    print(f"Core completeness: {core:.1%}")
    print(f"Rich completeness: {rich:.1%}")
    print(f"Closure score: {closure:.1%}")
    print()
    print("V1 vs V2 vs V3:")
    print(f"  Author:  0% →  0% → {has_author/n:.0%}")
    print(f"  Caption: 0% → 100% → {has_text/n:.0%}")
    print(f"  Hashtags:0% → 85% → {has_hashtags/n:.0%}")
    print(f"  Timestamp:0%→ 100% → {has_timestamp/n:.0%}")
    print(f"  Media:   0% →  0% → {has_media/n:.0%}")
    print(f"  Likes:   0% → 90% → {has_likes/n:.0%}")
    print(f"  Comments:0% → 10% → {has_comments/n:.0%}")
    print(f"  Views:   0% →  0% → {has_views/n:.0%}")

    # Decision
    if has_author/n >= 0.6 and has_media/n >= 0.6 and core >= 0.75:
        decision = "VIABLE"
    elif has_author/n >= 0.4 and has_media/n >= 0.4 and core >= 0.6:
        decision = "INCONCLUSIVE"
    else:
        decision = "NOT_VIABLE"

    print()
    print(f"DECISION: {decision}")

    # Save report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "enriched": n,
        "author_rate": has_author/n,
        "text_rate": has_text/n,
        "hashtag_rate": has_hashtags/n,
        "timestamp_rate": has_timestamp/n,
        "media_rate": has_media/n,
        "likes_rate": has_likes/n,
        "comments_rate": has_comments/n,
        "views_rate": has_views/n,
        "core_completeness": core,
        "rich_completeness": rich,
        "closure_score": closure,
        "decision": decision,
        "v1_v2_v3": {
            "author": f"0% → 0% → {has_author/n:.0%}",
            "caption": f"0% → 100% → {has_text/n:.0%}",
            "hashtags": f"0% → 85% → {has_hashtags/n:.0%}",
            "timestamp": f"0% → 100% → {has_timestamp/n:.0%}",
            "media_type": f"0% → 0% → {has_media/n:.0%}",
            "likes": f"0% → 90% → {has_likes/n:.0%}",
            "comments": f"0% → 10% → {has_comments/n:.0%}",
            "views": f"0% → 0% → {has_views/n:.0%}",
        },
    }
    (WORKSPACE / "artifacts" / "browser-discovery" / "v3" / "report.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )


def _normalize(p: dict) -> dict:
    return {
        "id": p.get("content_id"),
        "source": "instagram_browser_v3",
        "external_id": p.get("content_id"),
        "url": p.get("url"),
        "author": p.get("author"),
        "author_id": p.get("author_id"),
        "published_at": p.get("published_at"),
        "collected_at": p.get("collected_at"),
        "text": p.get("text"),
        "hashtags": p.get("hashtags", []),
        "media_type": p.get("media_type", "UNKNOWN"),
        "is_video": p.get("is_video"),
        "is_reel": p.get("is_reel"),
        "like_count": p.get("like_count"),
        "like_raw": p.get("like_raw"),
        "like_source": p.get("like_source"),
        "comment_count": p.get("comment_count"),
        "comment_raw": p.get("comment_raw"),
        "comment_source": p.get("comment_source"),
        "view_count": p.get("view_count"),
        "audio_reference": p.get("audio_reference"),
        "raw_metrics": {
            "like_count": p.get("like_count"),
            "comment_count": p.get("comment_count"),
            "view_count": p.get("view_count"),
        },
        "metadata": {"provider": "browser_v3", "scenario": p.get("scenario")},
    }


if __name__ == "__main__":
    asyncio.run(main())
