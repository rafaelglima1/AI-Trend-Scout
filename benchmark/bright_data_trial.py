from __future__ import annotations

import asyncio
import httpx
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.environ.get("BRIGHT_DATA_API_KEY", "")

ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS = ROOT / "artifacts"
RAW_DIR = ARTIFACTS / "raw-datasets" / "bright_data"
NORM_DIR = ARTIFACTS / "normalized-datasets" / "bright_data"
RAW_DIR.mkdir(parents=True, exist_ok=True)
NORM_DIR.mkdir(parents=True, exist_ok=True)


async def run_trial() -> dict:
    results = {
        "provider": "bright_data",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "api_key_prefix": API_KEY[:8] + "..." if API_KEY else "none",
        "scenarios_tested": [],
        "total_records": 0,
        "errors": [],
    }

    scenarios = [
        {"id": "hashtag_discovery", "name": "Hashtag Discovery", "url": "https://www.instagram.com/explore/tags/fitness/"},
        {"id": "reels_discovery", "name": "Reels Discovery", "url": "https://www.instagram.com/reels/"},
        {"id": "posts_discovery", "name": "Posts Discovery", "url": "https://www.instagram.com/"},
    ]

    for scenario in scenarios:
        print(f"\n=== Testing: {scenario['name']} ===")
        result = await test_scenario(scenario)
        results["scenarios_tested"].append(result)
        results["total_records"] += result.get("records_returned", 0)

        if result.get("error"):
            results["errors"].append({"scenario": scenario["id"], "error": result["error"]})

    return results


async def test_scenario(scenario: dict) -> dict:
    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()

    result = {
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "started_at": started_at,
        "status": "NOT_SUPPORTED",
        "records_returned": 0,
        "error": None,
        "raw_response": None,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Try Bright Data SERP API
            resp = await client.post(
                "https://api.brightdata.com/serp/request",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "zone": "serp_api1",
                    "url": scenario["url"],
                    "format": "json",
                },
            )

            result["raw_response"] = {
                "status_code": resp.status_code,
                "response_preview": resp.text[:500] if resp.status_code != 200 else "success",
            }

            if resp.status_code == 200:
                data = resp.json()
                result["status"] = "SUCCESS"
                result["records_returned"] = len(data) if isinstance(data, list) else 0
            elif resp.status_code == 404:
                result["status"] = "NOT_SUPPORTED"
                result["error"] = "SERP API endpoint not found"
            elif resp.status_code == 401:
                result["status"] = "AUTH_FAILED"
                result["error"] = "Authentication failed"
            else:
                result["status"] = "ERROR"
                result["error"] = f"HTTP {resp.status_code}: {resp.text[:200]}"

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

    result["completed_at"] = datetime.now(timezone.utc).isoformat()
    result["duration_seconds"] = round(time.monotonic() - start_time, 2)

    print(f"  Status: {result['status']}")
    print(f"  Records: {result['records_returned']}")
    print(f"  Error: {result['error']}")

    return result


async def main() -> None:
    print("Phase -1.5: Bright Data Controlled Provider Trial")
    print("=" * 50)

    results = await run_trial()

    # Save results
    (ARTIFACTS / "bright-data-trial.json").write_text(
        json.dumps(results, indent=2, default=str), encoding="utf-8"
    )

    print("\n" + "=" * 50)
    print("Trial Complete")
    print(f"Total records: {results['total_records']}")
    print(f"Errors: {len(results['errors'])}")

    for err in results["errors"]:
        print(f"  - {err['scenario']}: {err['error']}")


if __name__ == "__main__":
    asyncio.run(main())
