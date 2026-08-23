from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any

from benchmark.providers import RawContent, DiscoveryResult
from benchmark.normalization import normalize, dedup_rate


@dataclass
class BenchmarkMetrics:
    provider: str
    scenario: str
    records_returned: int
    unique_records: int
    duplicate_rate: float
    freshness_rate: float
    metadata_completeness: float
    creator_diversity: float
    successful_runs: int
    total_runs: int
    latency_seconds: float
    cost_usd: float | None
    error: str | None


@dataclass
class DiscoveryQualityScore:
    freshness: float
    coverage: float
    metadata: float
    reliability: float
    diversity: float
    cost: float
    validation: float
    total: float


@dataclass
class TrendReadinessScore:
    temporal_data: float
    creator_diversity: float
    engagement_metrics: float
    deduplication_quality: float
    total: float


@dataclass
class EvidenceReadinessScore:
    source_reliability: float
    metadata_depth: float
    freshness: float
    repeatability: float
    total: float


def compute_metrics(result: DiscoveryResult, scenario_window_hours: int = 48) -> BenchmarkMetrics:
    contents = result.contents
    normalized = normalize(contents)

    dup_rate = dedup_rate(contents, normalized)
    freshness = _freshness_rate(normalized, scenario_window_hours)
    metadata_comp = _metadata_completeness(normalized)
    creator_div = _creator_diversity(normalized)

    return BenchmarkMetrics(
        provider=result.provider,
        scenario=result.scenario,
        records_returned=len(contents),
        unique_records=len(normalized),
        duplicate_rate=dup_rate,
        freshness_rate=freshness,
        metadata_completeness=metadata_comp,
        creator_diversity=creator_div,
        successful_runs=1 if result.error is None else 0,
        total_runs=1,
        latency_seconds=result.duration_seconds,
        cost_usd=result.cost_usd,
        error=result.error,
    )


def aggregate_metrics(metrics_list: list[BenchmarkMetrics]) -> BenchmarkMetrics:
    if not metrics_list:
        return BenchmarkMetrics(
            provider="none", scenario="none", records_returned=0,
            unique_records=0, duplicate_rate=0, freshness_rate=0,
            metadata_completeness=0, creator_diversity=0,
            successful_runs=0, total_runs=0, latency_seconds=0,
            cost_usd=None, error=None,
        )

    m = metrics_list
    return BenchmarkMetrics(
        provider=m[0].provider,
        scenario="aggregated",
        records_returned=sum(x.records_returned for x in m),
        unique_records=sum(x.unique_records for x in m),
        duplicate_rate=_avg([x.duplicate_rate for x in m]),
        freshness_rate=_avg([x.freshness_rate for x in m]),
        metadata_completeness=_avg([x.metadata_completeness for x in m]),
        creator_diversity=_avg([x.creator_diversity for x in m]),
        successful_runs=sum(x.successful_runs for x in m),
        total_runs=sum(x.total_runs for x in m),
        latency_seconds=_avg([x.latency_seconds for x in m]),
        cost_usd=sum(x.cost_usd for x in m if x.cost_usd) or None,
        error=None if all(x.error is None for x in m) else "partial_failure",
    )


def compute_discovery_quality(m: BenchmarkMetrics, has_validation: bool = False) -> DiscoveryQualityScore:
    freshness = m.freshness_rate * 100
    coverage = min(100, (m.unique_records / max(m.records_returned, 1)) * 100)
    metadata = m.metadata_completeness * 100
    reliability = (m.successful_runs / max(m.total_runs, 1)) * 100
    diversity = m.creator_diversity * 100
    cost_score = 80.0 if m.cost_usd is None or m.cost_usd < 10 else max(0, 100 - m.cost_usd)
    validation = 90.0 if has_validation else 50.0

    total = (
        freshness * 0.20
        + coverage * 0.20
        + metadata * 0.15
        + reliability * 0.15
        + diversity * 0.10
        + cost_score * 0.10
        + validation * 0.10
    )

    return DiscoveryQualityScore(
        freshness=round(freshness, 2),
        coverage=round(coverage, 2),
        metadata=round(metadata, 2),
        reliability=round(reliability, 2),
        diversity=round(diversity, 2),
        cost=round(cost_score, 2),
        validation=round(validation, 2),
        total=round(total, 2),
    )


def compute_trend_readiness(m: BenchmarkMetrics) -> TrendReadinessScore:
    temporal = min(100, m.freshness_rate * 100)
    creator = m.creator_diversity * 100
    has_engagement = 80.0 if m.records_returned > 0 else 0.0
    dedup = (1.0 - m.duplicate_rate) * 100

    total = (temporal * 0.35 + creator * 0.25 + has_engagement * 0.20 + dedup * 0.20)

    return TrendReadinessScore(
        temporal_data=round(temporal, 2),
        creator_diversity=round(creator, 2),
        engagement_metrics=round(has_engagement, 2),
        deduplication_quality=round(dedup, 2),
        total=round(total, 2),
    )


def compute_evidence_readiness(m: BenchmarkMetrics) -> EvidenceReadinessScore:
    source = (m.successful_runs / max(m.total_runs, 1)) * 100
    depth = m.metadata_completeness * 100
    freshness = m.freshness_rate * 100
    repeatability = min(100, m.total_runs / 3 * 100) if m.total_runs > 0 else 0

    total = (source * 0.30 + depth * 0.30 + freshness * 0.20 + repeatability * 0.20)

    return EvidenceReadinessScore(
        source_reliability=round(source, 2),
        metadata_depth=round(depth, 2),
        freshness=round(freshness, 2),
        repeatability=round(repeatability, 2),
        total=round(total, 2),
    )


def _freshness_rate(contents: list[RawContent], window_hours: int) -> float:
    if not contents:
        return 0.0
    now = datetime.now(timezone.utc)
    fresh = 0
    for c in contents:
        if not c.published_at:
            continue
        try:
            dt = datetime.fromisoformat(c.published_at.replace("Z", "+00:00"))
            if (now - dt).total_seconds() < window_hours * 3600:
                fresh += 1
        except (ValueError, TypeError):
            continue
    with_ts = sum(1 for c in contents if c.published_at)
    return fresh / max(with_ts, 1)


def _metadata_completeness(contents: list[RawContent]) -> float:
    if not contents:
        return 0.0
    essential_fields = ["external_id", "url", "author", "published_at", "text"]
    total_score = 0
    for c in contents:
        present = sum(1 for f in essential_fields if getattr(c, f, None))
        total_score += present / len(essential_fields)
    return total_score / len(contents)


def _creator_diversity(contents: list[RawContent]) -> float:
    if not contents:
        return 0.0
    authors = set(c.author for c in contents if c.author and c.author != "unknown")
    return len(authors) / max(len(contents), 1)


def _avg(values: list[float]) -> float:
    return sum(values) / max(len(values), 1)
