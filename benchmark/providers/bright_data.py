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


class BrightDataProvider:
    """Bright Data Instagram Collector — requires BRIGHT_DATA_API_KEY env var."""

    def __init__(self) -> None:
        self._api_key = os.environ.get("BRIGHT_DATA_API_KEY", "")
        self._zone = os.environ.get("BRIGHT_DATA_ZONE", "serp_api1")
        self._endpoint = os.environ.get(
            "BRIGHT_DATA_ENDPOINT",
            "https://api.brightdata.com/datasets/v3/trigger",
        )

    @property
    def name(self) -> str:
        return "bright_data"

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
        if not self._api_key:
            return ProviderHealth(status=SourceStatus.DOWN, message="No BRIGHT_DATA_API_KEY set")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                start = time.monotonic()
                resp = await client.get(
                    f"{self._endpoint}/errors",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    params={"zone": self._zone},
                )
                latency = (time.monotonic() - start) * 1000
                if resp.status_code in (200, 404):
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

        if not self._api_key:
            error = "BRIGHT_DATA_API_KEY not configured"
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
            async with httpx.AsyncClient(timeout=60) as client:
                payload = {
                    "zone": self._zone,
                    "url": f"https://www.instagram.com/explore/tags/{query.keywords[0].strip('#')}/" if query.keywords else "https://www.instagram.com/explore/reels/",
                    "format": "json",
                }
                resp = await client.post(
                    self._endpoint,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                raw_response["trigger"] = resp.json() if resp.status_code in (200, 201) else {"error": resp.status_code, "body": resp.text[:500]}

                if resp.status_code in (200, 201):
                    dataset_id = resp.json().get("dataset_id")
                    if dataset_id:
                        import asyncio
                        await asyncio.sleep(5)
                        snap_resp = await client.get(
                            f"https://api.brightdata.com/datasets/v3/snapshot/{dataset_id}",
                            headers={"Authorization": f"Bearer {self._api_key}"},
                            params={"format": "json"},
                        )
                        raw_response["snapshot"] = snap_resp.json() if snap_resp.status_code == 200 else {"error": snap_resp.status_code}
                        if snap_resp.status_code == 200:
                            for item in snap_resp.json() if isinstance(snap_resp.json(), list) else []:
                                contents.append(_parse_bright_data_item(item, query))
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


def _parse_bright_data_item(item: dict, query: DiscoveryQuery) -> RawContent:
    return RawContent(
        id=f"bd_{item.get('id', item.get('post_id', ''))}",
        source="instagram",
        external_id=item.get("id", item.get("post_id", "")),
        url=item.get("url", item.get("permalink", "")),
        author=item.get("author", item.get("owner_username", "unknown")),
        published_at=item.get("timestamp", item.get("taken_at")),
        collected_at=_now_iso(),
        text=item.get("caption", item.get("text", "")),
        media_type=item.get("media_type", item.get("type", "unknown")),
        media_reference=item.get("media_url", item.get("image_url")),
        hashtags=item.get("hashtags", []),
        audio_reference=item.get("music", item.get("audio")),
        raw_metrics={
            "like_count": item.get("likes", item.get("like_count")),
            "comments_count": item.get("comments", item.get("comments_count")),
            "view_count": item.get("play_count", item.get("views")),
        },
        metadata={"provider": "bright_data", "raw_item": item},
    )


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
