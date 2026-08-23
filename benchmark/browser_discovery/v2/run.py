from __future__ import annotations

import asyncio
import json
from pathlib import Path

from benchmark.browser_discovery.v2.enrichment import run_v2, SCENARIOS
from benchmark.browser_discovery.v2.report import generate_v2_report

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery" / "v2"
RAW = ARTIFACTS / "raw"
NORM = ARTIFACTS / "normalized"
RAW.mkdir(parents=True, exist_ok=True)
NORM.mkdir(parents=True, exist_ok=True)


async def main() -> None:
    print("=" * 60)
    print("  BROWSER DISCOVERY POC V2")
    print("  Post-Level Metadata Enrichment")
    print("=" * 60)
    print()

    results = await run_v2()

    enriched = results.get("all_enriched", [])

    for scenario in SCENARIOS:
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


def _normalize(post: dict) -> dict:
    return {
        "id": post.get("content_id"),
        "source": "instagram_browser",
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
        "metadata": {
            "provider": "browser",
            "scenario": post.get("scenario"),
            "status": post.get("status"),
        },
    }


if __name__ == "__main__":
    asyncio.run(main())
