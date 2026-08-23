from __future__ import annotations

from dataclasses import dataclass, field

from benchmark.trend_detection.content_intelligence import ContentFeatures


@dataclass
class Evidence:
    id: str
    content_id: str
    source: str
    signal_type: str
    observed_at: str
    description: str
    strength: float


def generate_evidence(
    contents: list[ContentFeatures],
    pattern_type: str,
    pattern_value: str,
    source_label: str,
) -> list[Evidence]:
    evidence = []

    for idx, c in enumerate(contents):
        signal = _detect_signal(c, pattern_type, pattern_value)
        if signal:
            evidence.append(Evidence(
                id=f"ev_{source_label}_{idx:04d}",
                content_id=c.content_id,
                source=source_label,
                signal_type=pattern_type,
                observed_at=c.published_at or "",
                description=signal,
                strength=0.8 if c.has_engagement else 0.5,
            ))

    return evidence


def _detect_signal(c: ContentFeatures, pattern_type: str, pattern_value: str) -> str | None:
    if pattern_type == "hashtag" and pattern_value in c.hashtag_set:
        return f"Content uses hashtag #{pattern_value}"
    elif pattern_type == "format" and c.media_type == pattern_value:
        return f"Content uses format {pattern_value}"
    elif pattern_type == "structure" and pattern_value in _get_structure(c):
        return f"Content has structure: {pattern_value}"
    elif pattern_type == "engagement":
        if pattern_value == "has_question" and c.has_question:
            return "Content contains a question"
        elif pattern_value == "has_number" and c.has_number:
            return "Content contains numbers/lists"
        elif pattern_value == "has_cta" and c.has_cta:
            return "Content contains a call to action"
    elif pattern_type == "language":
        if pattern_value in c.language_hints:
            return f"Content written in {pattern_value}"
    return None


def _get_structure(c: ContentFeatures) -> str:
    parts = []
    if c.has_question:
        parts.append("question")
    if c.has_number:
        parts.append("number")
    if c.has_cta:
        parts.append("cta")
    if c.word_count > 50:
        parts.append("long")
    elif c.word_count < 10:
        parts.append("short")
    else:
        parts.append("medium")
    return "_".join(parts) if parts else "generic"
