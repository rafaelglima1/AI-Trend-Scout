from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class DiscoveryMode(str, Enum):
    EXPLORATION = "exploration"
    MONITORING = "monitoring"
    VALIDATION = "validation"


class SourceStatus(str, Enum):
    UP = "up"
    DEGRADED = "degraded"
    DOWN = "down"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RawContent:
    id: str
    source: str
    external_id: str
    url: str
    author: str
    published_at: str | None
    collected_at: str
    text: str
    media_type: str
    media_reference: str | None
    hashtags: list[str]
    audio_reference: str | None
    raw_metrics: dict[str, Any]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class DiscoveryQuery:
    source: str
    mode: DiscoveryMode
    keywords: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    language: str | None = None
    region: str | None = None
    content_type: str | None = None
    limit: int = 100
    cursor: str | None = None
    profile_url: str | None = None


@dataclass(frozen=True)
class DiscoveryResult:
    provider: str
    scenario: str
    query: DiscoveryQuery
    contents: list[RawContent]
    raw_response: dict[str, Any]
    collected_at: str
    duration_seconds: float
    error: str | None = None
    cost_usd: float | None = None


@dataclass(frozen=True)
class ProviderHealth:
    status: SourceStatus
    message: str = ""
    latency_ms: float | None = None


@dataclass(frozen=True)
class ProviderCapabilities:
    search: bool = False
    discovery: bool = False
    author_metadata: bool = False
    metrics: bool = False
    publication_date: bool = False
    media: bool = False
    audio: bool = False
    hashtags: bool = False
    pagination: bool = False
    historical_data: bool = False


class DiscoveryProvider(Protocol):
    @property
    def name(self) -> str: ...

    async def discover(self, query: DiscoveryQuery) -> DiscoveryResult: ...

    async def health_check(self) -> ProviderHealth: ...

    def capabilities(self) -> ProviderCapabilities: ...
