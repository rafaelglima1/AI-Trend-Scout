from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BrowserMetrics:
    records_returned: int
    unique_records: int
    unique_creators: int
    duplicate_rate: float
    freshness_rate: float | None
    metadata_completeness: float
    creator_diversity: float
    timestamp_availability: float
    hashtag_availability: float
    author_availability: float
    text_availability: float
    like_count_availability: float
    comment_count_availability: float
    view_count_availability: float
    video_rate: float
    reel_rate: float
    scenario_success_rate: float
    browser_duration_seconds: float
    blocked: bool
    auth_required: bool
    captcha: bool


def compute_metrics(
    contents: list[dict],
    total_scenarios: int,
    successful_scenarios: int,
    duration: float,
    blocked: bool,
    auth_required: bool,
    captcha: bool,
) -> BrowserMetrics:
    unique_records = len(contents)
    unique_creators = len(set(c.get("author") for c in contents if c.get("author")))

    timestamps = [c for c in contents if c.get("published_at")]
    hashtags = [c for c in contents if c.get("hashtags")]
    authors = [c for c in contents if c.get("author")]
    texts = [c for c in contents if c.get("text")]
    likes = [c for c in contents if c.get("like_count") is not None]
    comments = [c for c in contents if c.get("comment_count") is not None]
    views = [c for c in contents if c.get("view_count") is not None]
    videos = [c for c in contents if c.get("media_type") in ("video", "reel")]
    reels = [c for c in contents if c.get("media_type") == "reel"]

    expected_fields = ["author", "published_at", "text", "hashtags", "media_type"]
    field_availability = 0
    for c in contents:
        present = sum(1 for f in expected_fields if c.get(f))
        field_availability += present / len(expected_fields)
    metadata_completeness = field_availability / max(len(contents), 1)

    freshness_rate = None
    if timestamps:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        fresh = 0
        for c in timestamps:
            try:
                dt = datetime.fromisoformat(c["published_at"].replace("Z", "+00:00"))
                if (now - dt).total_seconds() < 48 * 3600:
                    fresh += 1
            except Exception:
                pass
        freshness_rate = fresh / max(len(timestamps), 1)

    return BrowserMetrics(
        records_returned=unique_records,
        unique_records=unique_records,
        unique_creators=unique_creators,
        duplicate_rate=0.0,
        freshness_rate=freshness_rate,
        metadata_completeness=metadata_completeness,
        creator_diversity=unique_creators / max(unique_records, 1),
        timestamp_availability=len(timestamps) / max(unique_records, 1),
        hashtag_availability=len(hashtags) / max(unique_records, 1),
        author_availability=len(authors) / max(unique_records, 1),
        text_availability=len(texts) / max(unique_records, 1),
        like_count_availability=len(likes) / max(unique_records, 1),
        comment_count_availability=len(comments) / max(unique_records, 1),
        view_count_availability=len(views) / max(unique_records, 1),
        video_rate=len(videos) / max(unique_records, 1),
        reel_rate=len(reels) / max(unique_records, 1),
        scenario_success_rate=successful_scenarios / max(total_scenarios, 1),
        browser_duration_seconds=duration,
        blocked=blocked,
        auth_required=auth_required,
        captcha=captcha,
    )
