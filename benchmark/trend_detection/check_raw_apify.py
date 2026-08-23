import asyncio
import httpx
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
TOKEN = os.environ.get("APIFY_API_TOKEN", "")


async def main():
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            "https://api.apify.com/v2/acts/apify~instagram-scraper/runs",
            params={"token": TOKEN},
            json={
                "directUrls": ["https://www.instagram.com/explore/tags/fitness/"],
                "resultsLimit": 5,
                "resultsType": "posts",
            },
        )

        run_id = resp.json().get("data", {}).get("id")
        print(f"Run ID: {run_id}")

        for _ in range(20):
            await asyncio.sleep(5)
            status_resp = await client.get(
                f"https://api.apify.com/v2/actor-runs/{run_id}",
                params={"token": TOKEN},
            )
            status = status_resp.json().get("data", {}).get("status")
            if status in ("SUCCEEDED", "FAILED"):
                dataset_id = status_resp.json().get("data", {}).get("defaultDatasetId")
                items_resp = await client.get(
                    f"https://api.apify.com/v2/datasets/{dataset_id}/items",
                    params={"token": TOKEN, "format": "json"},
                )
                items = items_resp.json()
                print(f"Items: {len(items)}")
                if items:
                    print(f"\nFirst item keys: {list(items[0].keys())}")
                    print(f"\nFirst item:")
                    print(json.dumps(items[0], indent=2))
                break


asyncio.run(main())
