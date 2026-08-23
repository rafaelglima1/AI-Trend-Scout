from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass

from benchmark.trend_detection.content_intelligence import ContentFeatures


@dataclass
class TemporalSignal:
    content_count: int
    unique_creators: int
    first_seen: str
    last_seen: str
    span_hours: float
    creator_adoption_count: int
    unique_hashtags: int
    has_temporal_data: bool
    creator_list: list[str]


def compute_temporal_signal(contents: list[ContentFeatures]) -> TemporalSignal:
    timestamps: list[datetime] = []
    for c in contents:
        if c.published_at:
            try:
                dt = datetime.fromisoformat(c.published_at.replace("Z", "+00:00"))
                timestamps.append(dt)
            except (ValueError, TypeError):
                pass

    creators = list(set(c.author for c in contents if c.author and c.author != "unknown"))
    all_hashtags: set[str] = set()
    for c in contents:
        all_hashtags.update(c.hashtag_set)

    if timestamps:
        timestamps.sort()
        first = timestamps[0]
        last = timestamps[-1]
        span = (last - first).total_seconds() / 3600
        first_iso = first.isoformat()
        last_iso = last.isoformat()
    else:
        span = 0
        first_iso = ""
        last_iso = ""

    return TemporalSignal(
        content_count=len(contents),
        unique_creators=len(creators),
        first_seen=first_iso,
        last_seen=last_iso,
        span_hours=span,
        creator_adoption_count=len(creators),
        unique_hashtags=len(all_hashtags),
        has_temporal_data=len(timestamps) > 0,
        creator_list=creators,
    )
