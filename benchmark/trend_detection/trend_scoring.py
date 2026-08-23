from __future__ import annotations

from dataclasses import dataclass, field

from benchmark.trend_detection.content_intelligence import ContentFeatures
from benchmark.trend_detection.clustering import ClusterData
from benchmark.trend_detection.temporal import TemporalSignal
from benchmark.trend_detection.pattern_detection import PatternAnalysis
from benchmark.trend_detection.evidence import Evidence


@dataclass
class TrendCandidate:
    id: str
    pattern: str
    pattern_type: str
    lifecycle: str
    first_observed_at: str
    last_observed_at: str
    content_count: int
    unique_creator_count: int
    niche_count: int
    growth_signal: float
    engagement_signal: float
    replication_signal: float
    cross_niche_signal: float
    trend_score: float
    confidence: float
    evidence: list[Evidence]
    contents: list[str]
    primary_hashtags: list[str]
    dominant_format: str
    explanation: str


def compute_trend_score(
    temporal: TemporalSignal | None,
    content_count: int,
    unique_creators: int,
    niche_count: int,
    has_engagement: bool,
    has_temporal_data: bool,
) -> tuple[float, float]:
    growth = 0.0
    if has_temporal_data and temporal is not None and temporal.span_hours > 0:
        rate = content_count / max(temporal.span_hours, 1)
        growth = min(1.0, rate * 10)
    elif has_temporal_data:
        growth = 0.5

    adoption = min(1.0, unique_creators / 5.0)

    recency = 0.0
    if has_temporal_data and temporal is not None and temporal.has_temporal_data:
        recency = 0.8
    elif has_temporal_data:
        recency = 0.5

    cross_niche = min(1.0, niche_count / 3.0)

    engagement = 0.5 if has_engagement else 0.2

    similarity = min(1.0, content_count / 5.0)

    adaptability = min(1.0, (unique_creators + niche_count) / 6.0)

    score = (
        growth * 0.25
        + adoption * 0.20
        + recency * 0.15
        + cross_niche * 0.10
        + engagement * 0.10
        + similarity * 0.10
        + adaptability * 0.10
    )

    confidence_evidence_count = min(content_count, 10) / 10.0
    confidence_creator_diversity = min(1.0, unique_creators / 4.0)
    confidence_temporal = 0.8 if has_temporal_data else 0.2

    confidence = (
        confidence_evidence_count * 0.40
        + confidence_creator_diversity * 0.35
        + confidence_temporal * 0.25
    )

    return round(score * 100, 2), round(confidence * 100, 2)


def determine_lifecycle(
    content_count: int,
    unique_creators: int,
    growth_signal: float,
    confidence: float,
    temporal: TemporalSignal | None,
) -> str:
    if content_count < 2:
        return "INSUFFICIENT_EVIDENCE"

    if content_count == 1:
        return "VIRAL_SINGLE"

    if confidence < 30:
        return "INSUFFICIENT_EVIDENCE"

    if unique_creators >= 4 and content_count >= 5 and growth_signal > 0.5:
        return "GROWING"

    if unique_creators >= 2 and content_count >= 3:
        return "EMERGING"

    if unique_creators >= 5 and content_count >= 10:
        return "MAINSTREAM"

    return "EMERGING"
