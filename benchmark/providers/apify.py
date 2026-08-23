from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

import httpx

from benchmark.providers import (
    DiscoveryProvider,
    DiscoveryQuery,
    DiscoveryResult,
    ProviderCapabilities,
    ProviderHealth,
    RawContent,
    SourceStatus,
)


class ApifyProvider:
    """Apify Instagram Actors — requires APIFY_API_TOKEN env var."""

    ACTOR_DISCOVERY = "apify~instagram-scraper"
    ACTOR_PROFILE = "apify~instagram-scraper"

    def __init__(self) -> None:
        self._token = os.environ.get("APIFY_API_TOKEN", "")
        self._base_url = "https://api.apify.com/v2"

    @property
    def name(self) -> str:
        return "apify"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            search=True,
            discovery=True,
            author_metadata=True,
            metrics=True,
            publication_date=True,
            media=True,
            audio=True,
            hashtags=True,
            pagination=True,
            historical_data=False,
        )

    async def health_check(self) -> ProviderHealth:
        if not self._token:
            return ProviderHealth(status=SourceStatus.DOWN, message="No APIFY_API_TOKEN set")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                start = time.monotonic()
                resp = await client.get(
                    f"{self._base_url}/acts",
                    params={"token": self._token, "limit": 1},
                )
                latency = (time.monotonic() - start) * 1000
                if resp.status_code == 200:
                    return ProviderHealth(status=SourceStatus.UP, latency_ms=latency)
                return ProviderHealth(status=SourceStatus.DEGRADED, message=f"HTTP {resp.status_code}")
        except Exception as e:
            return ProviderHealth(status=SourceStatus.DOWN, message=str(e))

    async def discover(self, query: DiscoveryQuery) -> DiscoveryResult:
        collected_at = _now_iso()
        start = time.monotonic()
        error = None
        contents: list[RawContent] = []
        raw_response: dict = {}

        if not self._token:
            error = "APIFY_API_TOKEN not configured"
            return DiscoveryResult(
                provider=self.name,
                scenario="",
                query=query,
                contents=[],
                raw_response={},
                collected_at=collected_at,
                duration_seconds=time.monotonic() - start,
                error=error,
            )

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                if query.profile_url:
                    run_input = {
                        "directUrls": [query.profile_url],
                        "resultsLimit": query.limit,
                        "resultsType": "posts",
                    }
                    actor_id = self.ACTOR_PROFILE
                else:
                    hashtags = query.keywords if query.keywords else ["trending"]
                    run_input = {
                        "directUrls": [f"https://www.instagram.com/explore/tags/{h.strip('#')}/" for h in hashtags[:3]],
                        "resultsLimit": query.limit,
                        "resultsType": "posts",
                    }
                    actor_id = self.ACTOR_DISCOVERY

                resp = await client.post(
                    f"{self._base_url}/acts/{actor_id}/runs",
                    params={"token": self._token},
                    json=run_input,
                )
                raw_response["run_trigger"] = resp.json() if resp.status_code in (200, 201) else {"error": resp.status_code}

                if resp.status_code in (200, 201):
                    run_id = resp.json().get("data", {}).get("id")
                    if run_id:
                        import asyncio
                        await asyncio.sleep(10)
                        status_resp = await client.get(
                            f"{self._base_url}/actor-runs/{run_id}",
                            params={"token": self._token},
                        )
                        raw_response["run_status"] = status_resp.json() if status_resp.status_code == 200 else {"error": status_resp.status_code}

                        if status_resp.status_code == 200:
                            dataset_id = status_resp.json().get("data", {}).get("defaultDatasetId")
                            if dataset_id:
                                items_resp = await client.get(
                                    f"{self._base_url}/datasets/{dataset_id}/items",
                                    params={"token": self._token, "format": "json"},
                                )
                                raw_response["items"] = items_resp.json()[:5] if items_resp.status_code == 200 and isinstance(items_resp.json(), list) else []
                                if items_resp.status_code == 200 and isinstance(items_resp.json(), list):
                                    for item in items_resp.json():
                                        contents.append(_parse_apify_item(item))
        except Exception as e:
            error = str(e)

        return DiscoveryResult(
            provider=self.name,
            scenario="",
            query=query,
            contents=contents,
            raw_response=raw_response,
            collected_at=collected_at,
            duration_seconds=time.monotonic() - start,
            error=error,
        )


def _parse_apify_item(item: dict) -> RawContent:
    return RawContent(
        id=f"apify_{item.get('id', item.get('shortCode', ''))}",
        source="instagram",
        external_id=item.get("id", item.get("shortCode", "")),
        url=item.get("url", item.get("inputUrl", "")),
        author=item.get("ownerUsername", item.get("author", "unknown")),
        published_at=item.get("timestamp", item.get("takenAt")),
        collected_at=_now_iso(),
        text=item.get("caption", item.get("text", "")),
        media_type=item.get("type", item.get("mediaType", "unknown")),
        media_reference=item.get("videoUrl", item.get("imageUrl")),
        hashtags=item.get("hashtags", []),
        audio_reference=item.get("music", item.get("audio")),
        raw_metrics={
            "like_count": item.get("likesCount", item.get("likes")),
            "comments_count": item.get("commentsCount", item.get("comments")),
            "view_count": item.get("playCount", item.get("videoViewCount")),
        },
        metadata={"provider": "apify", "raw_item": item},
    )


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
