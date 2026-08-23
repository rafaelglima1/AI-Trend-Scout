from __future__ import annotations

from datetime import datetime, timezone


def normalize_contents(raw_contents: list[dict], scenario_id: str) -> list[dict]:
    normalized = []
    seen_ids: set[str] = set()

    for raw in raw_contents:
        content_id = raw.get("id", "")
        url = raw.get("url", "")

        dedup_key = content_id or url
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)

        normalized.append({
            "id": f"browser_{scenario_id}_{content_id}",
            "source": "instagram_browser",
            "external_id": content_id,
            "url": url,
            "author": raw.get("author"),
            "author_id": raw.get("author_id"),
            "published_at": raw.get("published_at"),
            "collected_at": raw.get("collected_at", datetime.now(timezone.utc).isoformat()),
            "text": raw.get("text", ""),
            "hashtags": _extract_hashtags(raw.get("text", "")),
            "media_type": _normalize_media_type(raw.get("media_type", "unknown")),
            "is_video": raw.get("media_type") in ("video", "reel"),
            "is_reel": raw.get("media_type") == "reel",
            "like_count": raw.get("like_count"),
            "comment_count": raw.get("comment_count"),
            "view_count": raw.get("view_count"),
            "audio_reference": raw.get("audio_reference"),
            "raw_metrics": {
                "like_count": raw.get("like_count"),
                "comment_count": raw.get("comment_count"),
                "view_count": raw.get("view_count"),
            },
            "metadata": {
                "provider": "browser",
                "scenario": scenario_id,
                "image_url": raw.get("image_url"),
            },
        })

    return normalized


def _extract_hashtags(text: str) -> list[str]:
    if not text:
        return []
    import re
    return list(set(re.findall(r"#(\w+)", text)))


def _normalize_media_type(mt: str) -> str:
    mapping = {
        "video": "video",
        "reel": "reel",
        "image": "image",
        "carousel": "carousel",
        "sidecar": "carousel",
    }
    return mapping.get(mt.lower(), "unknown") if mt else "unknown"
