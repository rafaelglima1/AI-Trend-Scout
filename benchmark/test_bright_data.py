import asyncio
import httpx
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.environ.get("BRIGHT_DATA_API_KEY", "")


async def test_bright_data():
    print(f"API Key: {API_KEY[:8]}..." if API_KEY else "No key")
    print()

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        # Try Bright Data's Web Unlocker API
        print("=== Testing Web Unlocker API ===")
        print()

        # Try different Web Unlocker endpoints
        endpoints = [
            # Web Unlocker request
            ("POST", "https://api.brightdata.com/web_unlocker/v1/request", {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }),
            # Web Unlocker zones
            ("GET", "https://api.brightdata.com/web_unlocker/v1/zones", {
                "Authorization": f"Bearer {API_KEY}",
            }),
            # Scraping Browser
            ("POST", "https://api.brightdata.com/scraping/browser/v1/request", {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }),
            # SERP API with different format
            ("POST", "https://api.brightdata.com/serp/v1/request", {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }),
        ]

        for method, url, headers in endpoints:
            try:
                if method == "POST":
                    resp = await client.post(url, headers=headers, json={
                        "zone": "serp_api1",
                        "url": "https://www.instagram.com/explore/tags/fitness/",
                    })
                else:
                    resp = await client.get(url, headers=headers)
                print(f"{method} {url}")
                print(f"  Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"  Response: {resp.text[:300]}")
                else:
                    print(f"  Response: {resp.text[:150]}")
                print()
            except Exception as e:
                print(f"  Error: {e}")
                print()

        # Try to use the key directly as a proxy
        print("=== Testing Direct Proxy ===")
        try:
            # Bright Data proxy with API key as password
            proxy_url = f"http://brd-customer-hl_{API_KEY[:8]}-zone-serp_api1:{API_KEY}@brd.superproxy.io:22225"
            print(f"Proxy URL: http://brd-customer-hl_...@brd.superproxy.io:22225")

            async with httpx.AsyncClient(proxy=proxy_url, timeout=15) as proxy_client:
                resp = await proxy_client.get("https://httpbin.org/ip")
                print(f"  Status: {resp.status_code}")
                print(f"  Response: {resp.text[:200]}")
        except Exception as e:
            print(f"  Error: {e}")


asyncio.run(test_bright_data())
