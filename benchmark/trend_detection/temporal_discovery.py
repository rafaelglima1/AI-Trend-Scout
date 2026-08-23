from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

import httpx

ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOTS_DIR = ROOT / "artifacts" / "temporal-snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

TOKEN = os.environ.get("APIFY_API_TOKEN", "")

SNAPSHOT_CONFIGS = [
    {"keywords": ["fitness"], "label": "fitness_only"},
    {"keywords": ["fitness", "treino"], "label": "fitness_treino"},
    {"keywords": ["fitness", "treino", "academia"], "label": "fitness_treino_academia"},
    {"keywords": ["fitness", "treino", "academia", "workout"], "label": "fitness_treino_academia_workout"},
]

INTERVAL_SECONDS = 10


async def run_discovery(snapshot_idx: int, config: dict) -> dict:
    started_at = datetime.now(timezone.utc).isoformat()
    contents = []
    error = None

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            hashtags = config["keywords"]
            direct_urls = [f"https://www.instagram.com/explore/tags/{h}/" for h in hashtags]

            resp = await client.post(
                "https://api.apify.com/v2/acts/apify~instagram-scraper/runs",
                params={"token": TOKEN},
                json={
                    "directUrls": direct_urls,
                    "resultsLimit": 30,
                    "resultsType": "posts",
                },
            )

            if resp.status_code not in (200, 201):
                error = f"HTTP {resp.status_code}"
                return _make_result(snapshot_idx, config, started_at, [], error)

            run_id = resp.json().get("data", {}).get("id")
            if not run_id:
                error = "No run ID"
                return _make_result(snapshot_idx, config, started_at, [], error)

            for _ in range(20):
                await asyncio.sleep(5)
                status_resp = await client.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}",
                    params={"token": TOKEN},
                )
                if status_resp.status_code == 200:
                    status = status_resp.json().get("data", {}).get("status")
                    if status in ("SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"):
                        if status != "SUCCEEDED":
                            error = f"Run {status}"
                            return _make_result(snapshot_idx, config, started_at, [], error)

                        dataset_id = status_resp.json().get("data", {}).get("defaultDatasetId")
                        if dataset_id:
                            items_resp = await client.get(
                                f"https://api.apify.com/v2/datasets/{dataset_id}/items",
                                params={"token": TOKEN, "format": "json"},
                            )
                            if items_resp.status_code == 200:
                                for item in items_resp.json():
                                    contents.append(_normalize_item(item))
                        break

    except Exception as e:
        error = str(e)

    return _make_result(snapshot_idx, config, started_at, contents, error)


def _normalize_item(item: dict) -> dict:
    return {
        "id": str(item.get("id", "")),
        "external_id": str(item.get("id", "")),
        "url": item.get("url", ""),
        "author": item.get("ownerUsername", "unknown"),
        "author_name": item.get("ownerFullName", ""),
        "author_id": item.get("ownerId", ""),
        "published_at": item.get("timestamp"),
        "text": item.get("caption", ""),
        "media_type": item.get("type", "unknown"),
        "hashtags": [h for h in item.get("hashtags", []) if not h[0].isdigit()],
        "raw_metrics": {
            "like_count": item.get("likesCount"),
            "comments_count": item.get("commentsCount"),
        },
    }


def _make_result(idx: int, config: dict, started_at: str, contents: list, error: str | None) -> dict:
    authors = set(c.get("author", "") for c in contents if c.get("author") != "unknown")
    return {
        "snapshot_id": f"T{idx}",
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "provider": "apify",
        "query": {"keywords": config["keywords"], "label": config["label"]},
        "content_count": len(contents),
        "unique_content_count": len(set(c.get("external_id", "") for c in contents)),
        "unique_creator_count": len(authors),
        "error": error,
        "contents": contents,
    }


async def main() -> None:
    print(f"Running {len(SNAPSHOT_CONFIGS)} discovery cycles...")
    print(f"Interval: {INTERVAL_SECONDS}s between snapshots")
    print("=" * 50)

    snapshots = []

    for idx, config in enumerate(SNAPSHOT_CONFIGS):
        print(f"\n--- Snapshot T{idx} ({config['label']}) ---")
        result = await run_discovery(idx, config)
        snapshots.append(result)

        path = SNAPSHOTS_DIR / f"snapshot_T{idx}.json"
        path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

        print(f"  Records: {result['content_count']}")
        print(f"  Unique: {result['unique_content_count']}")
        print(f"  Creators: {result['unique_creator_count']}")
        print(f"  Error: {result['error']}")

        if idx < len(SNAPSHOT_CONFIGS) - 1:
            print(f"  Waiting {INTERVAL_SECONDS}s...")
            await asyncio.sleep(INTERVAL_SECONDS)

    summary = {
        "total_snapshots": len(snapshots),
        "interval_seconds": INTERVAL_SECONDS,
        "snapshots": [
            {
                "id": s["snapshot_id"],
                "started_at": s["started_at"],
                "keywords": s["query"]["keywords"],
                "content_count": s["content_count"],
                "unique_content_count": s["unique_content_count"],
                "unique_creator_count": s["unique_creator_count"],
                "error": s["error"],
            }
            for s in snapshots
        ],
    }

    (ROOT / "artifacts" / "temporal-snapshots-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print("\n" + "=" * 50)
    print("Summary:")
    for s in summary["snapshots"]:
        print(f"  {s['id']}: {s['content_count']} records, {s['unique_creator_count']} creators, keywords={s['keywords']}")


if __name__ == "__main__":
    asyncio.run(main())
