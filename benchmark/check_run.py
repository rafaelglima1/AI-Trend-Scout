import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
token = os.environ.get("APIFY_API_TOKEN", "")


async def test():
    async with httpx.AsyncClient(timeout=60) as client:
        run_id = "65x914e1Cj9U1PpJU"
        print(f"Checking run {run_id}...")

        for i in range(10):
            await asyncio.sleep(5)
            status_resp = await client.get(
                f"https://api.apify.com/v2/actor-runs/{run_id}",
                params={"token": token},
            )
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                status = status_data.get("data", {}).get("status")
                print(f"Check {i+1}: Status = {status}")

                if status in ("SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"):
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
                                print(f"First item keys: {list(items[0].keys())[:15]}")
                                print(f"First item sample: {str(items[0])[:500]}")
                    break


asyncio.run(test())
