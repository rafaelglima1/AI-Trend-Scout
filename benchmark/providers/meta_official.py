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


class MetaOfficialProvider:
    """Instagram Graph API (Official) — requires META_ACCESS_TOKEN env var."""

    def __init__(self) -> None:
        self._token = os.environ.get("META_ACCESS_TOKEN", "")
        self._api_version = os.environ.get("META_API_VERSION", "v19.0")
        self._base_url = f"https://graph.facebook.com/{self._api_version}"

    @property
    def name(self) -> str:
        return "meta_official"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            search=True,
            discovery=False,
            author_metadata=True,
            metrics=True,
            publication_date=True,
            media=True,
            audio=False,
            hashtags=True,
            pagination=True,
            historical_data=False,
        )

    async def health_check(self) -> ProviderHealth:
        if not self._token:
            return ProviderHealth(status=SourceStatus.DOWN, message="No META_ACCESS_TOKEN set")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                start = time.monotonic()
                resp = await client.get(
                    f"{self._base_url}/debug_token",
                    params={"input_token": self._token, "access_token": self._token},
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
            error = "META_ACCESS_TOKEN not configured"
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
            async with httpx.AsyncClient(timeout=30) as client:
                for keyword in query.keywords:
                    hashtag = keyword.strip("#")
                    resp = await client.get(
                        f"{self._base_url}/ig_hashtag_search",
                        params={
                            "user_id": "me",
                            "q": hashtag,
                            "access_token": self._token,
                        },
                    )
                    raw_response[keyword] = resp.json() if resp.status_code == 200 else {"error": resp.status_code}

                    if resp.status_code == 200:
                        hashtag_id = resp.json().get("data", [{}])[0].get("id")
                        if hashtag_id:
                            media_resp = await client.get(
                                f"{self._base_url}/{hashtag_id}/recent_media",
                                params={
                                    "user_id": "me",
                                    "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
                                    "limit": min(query.limit, 50),
                                    "access_token": self._token,
                                },
                            )
                            if media_resp.status_code == 200:
                                for item in media_resp.json().get("data", []):
                                    contents.append(_parse_media_item(item, hashtag))
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


def _parse_media_item(item: dict, hashtag: str) -> RawContent:
    return RawContent(
        id=f"meta_{item.get('id', '')}",
        source="instagram",
        external_id=item.get("id", ""),
        url=item.get("permalink", ""),
        author=item.get("owner", {}).get("username", "unknown") if "owner" in item else "unknown",
        published_at=item.get("timestamp"),
        collected_at=_now_iso(),
        text=item.get("caption", ""),
        media_type=item.get("media_type", "unknown"),
        media_reference=item.get("media_url"),
        hashtags=[hashtag],
        audio_reference=None,
        raw_metrics={
            "like_count": item.get("like_count"),
            "comments_count": item.get("comments_count"),
        },
        metadata={"provider": "meta_official", "raw_item": item},
    )


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
