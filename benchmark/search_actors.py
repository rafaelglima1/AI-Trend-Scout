import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
token = os.environ.get("APIFY_API_TOKEN", "")


async def test():
    async with httpx.AsyncClient(timeout=30) as client:
        # Check token validity
        resp = await client.get(
            "https://api.apify.com/v2/users/me",
            params={"token": token},
        )
        print(f"User info status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            user = data.get("data", {})
            print(f"Username: {user.get('username')}")
            print(f"Plan: {user.get('plan')}")
            print(f"Usage: {user.get('usageTotalUsd')}")

        # Try to list my builds
        resp2 = await client.get(
            "https://api.apify.com/v2/acts",
            params={"token": token, "limit": 10},
        )
        print(f"\nMy acts status: {resp2.status_code}")
        if resp2.status_code == 200:
            data2 = resp2.json()
            items = data2.get("data", {}).get("items", [])
            print(f"My acts count: {len(items)}")
            for item in items:
                print(f"  {item.get('name')} - {item.get('id')}")

        # Try to search store with different approach
        resp3 = await client.get(
            "https://api.apify.com/v2/store",
            params={"limit": 10, "search": "instagram"},
        )
        print(f"\nPublic store search status: {resp3.status_code}")
        if resp3.status_code == 200:
            data3 = resp3.json()
            items3 = data3.get("items", [])
            print(f"Found {len(items3)} actors")
            for item in items3[:5]:
                print(f"  {item.get('username')}/{item.get('name')}")


asyncio.run(test())
