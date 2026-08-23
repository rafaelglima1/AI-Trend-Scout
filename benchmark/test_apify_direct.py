import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
token = os.environ.get("APIFY_API_TOKEN", "")


async def test():
    async with httpx.AsyncClient(timeout=60) as client:
        # Try to run instagram-scraper directly
        print("Trying to run apify/instagram-scraper...")
        resp = await client.post(
            "https://api.apify.com/v2/acts/apify~instagram-scraper/runs",
            params={"token": token},
            json={
                "directUrls": ["https://www.instagram.com/p/C1234567890/"],
                "resultsLimit": 5,
                "resultsType": "posts",
            },
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")

        if resp.status_code in (200, 201):
            run_data = resp.json()
            run_id = run_data.get("data", {}).get("id")
            if run_id:
                print(f"\nRun ID: {run_id}")
                print("Waiting for run to complete...")
                await asyncio.sleep(10)
                status_resp = await client.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}",
                    params={"token": token},
                )
                print(f"Status check: {status_resp.status_code}")
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    status = status_data.get("data", {}).get("status")
                    print(f"Run status: {status}")
                    dataset_id = status_data.get("data", {}).get("defaultDatasetId")
                    if dataset_id:
                        items_resp = await client.get(
                            f"https://api.apify.com/v2/datasets/{dataset_id}/items",
                            params={"token": token, "format": "json"},
                        )
                        if items_resp.status_code == 200:
                            items = items_resp.json()
                            print(f"Items count: {len(items)}")
                            if items:
                                print(f"First item keys: {list(items[0].keys())[:10]}")


asyncio.run(test())
