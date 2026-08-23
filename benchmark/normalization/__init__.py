from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from benchmark.providers import RawContent


def normalize(contents: list[RawContent]) -> list[RawContent]:
    normalized = []
    seen_hashes: set[str] = set()

    for c in contents:
        dedup_key = _dedup_key(c)
        if dedup_key in seen_hashes:
            continue
        seen_hashes.add(dedup_key)

        normalized.append(RawContent(
            id=c.id,
            source=c.source,
            external_id=c.external_id,
            url=_clean_url(c.url),
            author=_normalize_author(c.author),
            published_at=_normalize_timestamp(c.published_at),
            collected_at=c.collected_at,
            text=c.text.strip() if c.text else "",
            media_type=_normalize_media_type(c.media_type),
            media_reference=c.media_reference,
            hashtags=_normalize_hashtags(c.hashtags, c.text),
            audio_reference=c.audio_reference,
            raw_metrics=_normalize_metrics(c.raw_metrics),
            metadata={k: v for k, v in c.metadata.items() if k != "raw_item"},
        ))

    return normalized


def dedup_rate(original: list[RawContent], normalized: list[RawContent]) -> float:
    if not original:
        return 0.0
    return 1.0 - (len(normalized) / len(original))


def _dedup_key(c: RawContent) -> str:
    raw = f"{c.external_id}|{c.url}|{c.author}|{c.text[:100]}"
    return sha256(raw.encode()).hexdigest()


def _clean_url(url: str) -> str:
    if not url:
        return ""
    return url.split("?")[0].rstrip("/")


def _normalize_author(author: str) -> str:
    if not author:
        return "unknown"
    return author.strip().lstrip("@")


def _normalize_timestamp(ts: str | None) -> str | None:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.isoformat()
    except (ValueError, TypeError):
        return ts


def _normalize_media_type(mt: str) -> str:
    mapping = {
        "Video": "video",
        "Image": "image",
        "Carousel": "carousel",
        "reel": "video",
        "video": "video",
        "image": "image",
        "sidecar": "carousel",
    }
    return mapping.get(mt, mt.lower() if mt else "unknown")


def _normalize_hashtags(hashtags: list[str], text: str) -> list[str]:
    result = list(hashtags) if hashtags else []
    if text:
        import re
        found = re.findall(r"#(\w+)", text)
        for h in found:
            if h.lower() not in [x.lower() for x in result]:
                result.append(h.lower())
    return list(set(result))


def _normalize_metrics(metrics: dict) -> dict:
    normalized = {}
    for key, value in metrics.items():
        if value is None:
            normalized[key] = None
            continue
        try:
            normalized[key] = int(value)
        except (ValueError, TypeError):
            normalized[key] = value
    return normalized
