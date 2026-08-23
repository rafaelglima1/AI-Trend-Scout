import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
token = os.environ.get("APIFY_API_TOKEN", "")
print(f"Token: {token[:10]}..." if token else "No token")


async def test():
    async with httpx.AsyncClient(timeout=30) as client:
        # Try a simple search
        resp = await client.post(
            f"https://api.apify.com/v2/acts/apify~instagram-reels-scraper/runs",
            params={"token": token},
            json={"search": "fitness", "searchType": "hashtag", "resultsLimit": 10},
        )
        print(f"Run trigger status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")

        if resp.status_code in (200, 201):
            run_data = resp.json()
            run_id = run_data.get("data", {}).get("id")
            if run_id:
                print(f"Run ID: {run_id}")
                await asyncio.sleep(15)
                status_resp = await client.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}",
                    params={"token": token},
                )
                print(f"Status: {status_resp.status_code}")
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    dataset_id = status_data.get("data", {}).get("defaultDatasetId")
                    print(f"Dataset ID: {dataset_id}")
                    if dataset_id:
                        items_resp = await client.get(
                            f"https://api.apify.com/v2/datasets/{dataset_id}/items",
                            params={"token": token, "format": "json"},
                        )
                        print(f"Items status: {items_resp.status_code}")
                        if items_resp.status_code == 200:
                            items = items_resp.json()
                            print(f"Items count: {len(items)}")
                            if items:
                                print(f"First item keys: {list(items[0].keys())[:10]}")
                                print(f"First item sample: {str(items[0])[:300]}")


asyncio.run(test())
