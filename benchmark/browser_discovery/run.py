from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from benchmark.browser_discovery.v2.enrichment import run_v2, SCENARIOS as V2_SCENARIOS
from benchmark.browser_discovery.v2.extraction import (
    extract_author,
    extract_comment_count,
    extract_like_count,
    classify_media_type,
)

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery" / "v2"
RAW = ARTIFACTS / "raw"
NORM = ARTIFACTS / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORM.mkdir(parents=True, exist_ok=True)


def main() -> None:
    if "--v3" in sys.argv:
        asyncio.run(main_v3())
    else:
        asyncio.run(main_v2())


async def main_v2() -> None:
    print("=" * 60)
    print("  BROWSER DISCOVERY POC V2")
    print("  Post-Level Metadata Enrichment")
    print("=" * 60)
    print()

    from benchmark.browser_discovery.v2.enrichment import run_v2 as run_v2_orig

    results = await run_v2_orig()

    enriched = results.get("all_enriched", [])

    for scenario in V2_SCENARIOS:
        scenario_posts = [p for p in enriched if p.get("scenario") == scenario["id"]]
        path = RAW / f"{scenario['id']}.json"
        path.write_text(json.dumps(scenario_posts, indent=2, default=str), encoding="utf-8")

        normalized = [_normalize(p) for p in scenario_posts]
        npath = NORM / f"{scenario['id']}.json"
        npath.write_text(json.dumps(normalized, indent=2, default=str), encoding="utf-8")

    generate_v2_report(results, enriched)

    print()
    print("=" * 60)
    print(f"Attempted: {results.get('attempted_total', 0)}")
    print(f"Successful: {results.get('successful_total', 0)}")
    print(f"Enriched: {len(enriched)}")

    if enriched:
        has_author = sum(1 for p in enriched if p.get("author"))
        has_text = sum(1 for p in enriched if p.get("text"))
        has_likes = sum(1 for p in enriched if p.get("like_count") is not None)
        has_views = sum(1 for p in enriched if p.get("view_count") is not None)
        n = len(enriched)
        print(f"Author: {has_author}/{n} ({has_author/n:.0%})")
        print(f"Text: {has_text}/{n} ({has_text/n:.0%})")
        print(f"Likes: {has_likes}/{n} ({has_likes/n:.0%})")
        print(f"Views: {has_views}/{n} ({has_views/n:.0%})")

    print("=" * 60)
    print("Concluido.")


async def main_v3() -> None:
    print("=" * 60)
    print("  BROWSER DISCOVERY POC V3")
    print("  Metadata Closure")
    print("=" * 60)
    print()

    if not check_session_exists():
        print("No session found.")
        return

    all_enriched = []
    session = await get_session()

    async with create_playwright_browser() as browser:
        context = await browser.new_context(storage_state=session)
        page = await context.new_page()

        for scenario in V2_SCENARIOS:
            if len(all_enriched) >= 20:
                break

            listing = await get_listing(page, scenario)
            selected = listing[:15]
            limit = min(10, 20 - len(all_enriched))

            for url in selected[:limit]:
                post = await extract_post(page, url, scenario["id"])
                if post["status"] == "SUCCESS":
                    all_enriched.append(post)

        await browser.close()

    for scenario in V2_SCENARIOS:
        posts = [p for p in all_enriched if p.get("scenario") == scenario["id"]]
        path = RAW / f"{scenario['id']}.json"
        path.write_text(json.dumps(posts, indent=2, default=str), encoding="utf-8")

        normalized = [_normalize(p) for p in posts]
        npath = NORM / f"{scenario['id']}.json"
        npath.write_text(json.dumps(normalized, indent=2, default=str), encoding="utf-8")

    report_data = generate_v3_report(all_enriched)
    write_report(report_data, ARTIFACTS)

    print()
    print("=" * 60)
    print(f"Total enriched: {len(all_enriched)}")

    if all_enriched:
        n = len(all_enriched)
        has_author = sum(1 for p in all_enriched if p.get("author"))
        has_text = sum(1 for p in all_enriched if p.get("text"))
        has_hashtags = sum(1 for p in all_enriched if p.get("hashtags"))
        has_timestamp = sum(1 for p in all_enriched if p.get("published_at"))
        has_media = sum(1 for p in all_enriched if p.get("media_type") not in ("UNKNOWN", None))
        has_likes = sum(1 for p in all_enriched if p.get("like_count") is not None)
        has_comments = sum(1 for p in all_enriched if p.get("comment_count") is not None)
        has_views = sum(1 for p in all_enriched if p.get("view_count") is not None)

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
            (1 if p.get("media_type") not in ("UNKNOWN", None) else 0) +
            (1 if p.get("comment_count") is not None else 0)
            for p in all_enriched
        ) / (n * 3)

        print(f"Author: {has_author}/{n} ({has_author/n:.0%})")
        print(f"Text: {has_text}/{n} ({has_text/n:.0%})")
        print(f"Hashtags: {has_hashtags}/{n} ({has_hashtags/n:.0%})")
        print(f"Timestamp: {has_timestamp}/{n} ({has_timestamp/n:.0%})")
        print(f"Media type: {has_media}/{n} ({has_media/n:.0%})")
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

    print("=" * 60)
    print("Concluido.")


async def get_session() -> str:
    from playwright.async_api import async_playwright

    session_path = ROOT / "artifacts" / "browser-discovery" / "cache" / "instagram_session.json"
    return str(session_path)


def check_session_exists() -> bool:
    session_path = ROOT / "artifacts" / "browser-discovery" / "cache" / "instagram_session.json"
    return session_path.exists()


async def create_playwright_browser():
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    return browser


async def get_listing(page, scenario: dict) -> list[str]:
    urls, seen = [], set()
    try:
        await page.goto(scenario["url"], wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        for _ in range(3):
            links = await page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
            for link in links:
                href = await link.get_attribute("href")
                if href and href not in seen and len(urls) < 15:
                    seen.add(href)
                    urls.append(f"https://www.instagram.com{href}" if href.startswith("/") else href)
            if len(urls) >= 15:
                break
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(1)
    except Exception:
        pass
    return urls


async def extract_post(page, url: str, scenario_id: str) -> dict:
    result = {
        "url": url, "scenario": scenario_id, "status": "PENDING",
        "content_id": extract_content_id(url), "author": None, "author_id": None,
        "text": None, "published_at": None, "hashtags": [],
        "media_type": "UNKNOWN", "is_video": False, "is_reel": "/reel/" in url,
        "like_count": None, "comment_count": None, "view_count": None,
        "audio_reference": None, "collected_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2)

        if "login" in page.url.lower():
            result["status"] = "AUTH_REQUIRED"
            return result

        html = await page.content()

        og_desc = re.search(r'<meta\s+(?:name|property)="og:description"\s+content="([^"]+)"', html, re.IGNORECASE)
        text = og_desc.group(1) if og_desc else ""
        result["text"] = text[:500] if text else None

        result["author"] = extract_author(text)
        result["comment_count"] = extract_comment_count(text)
        result["like_count"] = extract_like_count(text)

        media_type, is_video, is_reel = classify_media_type(html, text, url)
        result["media_type"] = media_type
        result["is_video"] = is_video
        result["is_reel"] = is_reel

        result["hashtags"] = list(set(re.findall(r"#(\w+)", text)))

        ts_match = re.search(r'<time\s+datetime="([^"]+)"', html)
        if ts_match:
            result["published_at"] = ts_match.group(1)
        else:
            date_match = re.search(r"on\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
            if date_match:
                result["published_at"] = date_match.group(1)

        result["status"] = "SUCCESS"

    except Exception as e:
        result["status"] = "TIMEOUT" if "timeout" in str(e).lower() else "ERROR"
        result["error"] = str(e)[:200]

    return result


def extract_content_id(url: str) -> str:
    import re
    m = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", url)
    return m.group(2) if m else url.split("/")[-1] if "/" in url else url


def generate_v2_report(results, enriched):
    pass


def write_report(data, artifacts_dir):
    pass


def _normalize(post: dict) -> dict:
    return {
        "id": post.get("content_id"),
        "source": "instagram_browser_v3",
        "external_id": post.get("content_id"),
        "url": post.get("url"),
        "author": post.get("author"),
        "author_id": post.get("author_id"),
        "published_at": post.get("published_at"),
        "collected_at": post.get("collected_at"),
        "text": post.get("text") or post.get("caption"),
        "hashtags": post.get("hashtags", []),
        "media_type": post.get("media_type", "UNKNOWN"),
        "is_video": post.get("is_video"),
        "is_reel": post.get("is_reel"),
        "like_count": post.get("like_count"),
        "comment_count": post.get("comment_count"),
        "view_count": post.get("view_count"),
        "audio_reference": post.get("audio_reference"),
        "raw_metrics": {
            "like_count": post.get("like_count"),
            "comment_count": post.get("comment_count"),
            "view_count": post.get("view_count"),
        },
        "metadata": {"provider": "browser_v3", "scenario": post.get("scenario")},
    }


import re
from datetime import datetime, timezone


if __name__ == "__main__":
    main()
