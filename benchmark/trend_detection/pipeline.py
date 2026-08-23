from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

from benchmark.trend_detection.content_intelligence import extract_features, ContentFeatures
from benchmark.trend_detection.clustering import cluster_by_hashtag_similarity, cluster_by_text_similarity, ClusterResult
from benchmark.trend_detection.temporal import compute_temporal_signal, TemporalSignal
from benchmark.trend_detection.pattern_detection import detect_patterns, PatternAnalysis
from benchmark.trend_detection.evidence import generate_evidence, Evidence
from benchmark.trend_detection.trend_scoring import (
    TrendCandidate,
    compute_trend_score,
    determine_lifecycle,
)


def load_dataset(raw_dir: Path) -> list[dict]:
    contents = []
    seen_ids: set[str] = set()

    for f in raw_dir.glob("apify_*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        for c in data.get("contents", []):
            ext_id = c.get("external_id", c.get("id", ""))
            if ext_id and ext_id not in seen_ids:
                seen_ids.add(ext_id)
                contents.append(c)

    return contents


def run_pipeline(raw_dir: Path) -> dict:
    raw_contents = load_dataset(raw_dir)
    print(f"Loaded {len(raw_contents)} unique records")

    features = [extract_features(c) for c in raw_contents]
    print(f"Extracted features for {len(features)} contents")

    hashtag_cluster_result = cluster_by_hashtag_similarity(features, min_overlap=2)
    text_cluster_result = cluster_by_text_similarity(features, min_overlap=0.3)

    all_clusters = _merge_cluster_results(hashtag_cluster_result, text_cluster_result)
    print(f"Found {len(all_clusters)} clusters (noise: {sum(1 for c in features if not any(c.content_id in cl.contents for cl in all_clusters))})")

    trend_candidates: list[TrendCandidate] = []
    noise_count = 0

    for cluster in all_clusters:
        temporal = compute_temporal_signal(cluster.contents)
        patterns = detect_patterns(cluster.contents, temporal)

        content_count = len(cluster.contents)
        unique_creators = len(set(c.author for c in cluster.contents))
        niche_count = len(patterns.niche_signals)

        has_engagement = any(c.has_engagement for c in cluster.contents)
        has_temporal = temporal.has_temporal_data

        growth_signal = min(1.0, content_count / 5.0) if has_temporal else 0.0
        replication_signal = min(1.0, unique_creators / 4.0)
        cross_niche_signal = min(1.0, niche_count / 3.0)
        engagement_signal = 0.5 if has_engagement else 0.2

        score, confidence = compute_trend_score(
            temporal, content_count, unique_creators, niche_count,
            has_engagement, has_temporal,
        )

        lifecycle = determine_lifecycle(
            content_count, unique_creators, growth_signal, confidence, temporal,
        )

        if lifecycle == "INSUFFICIENT_EVIDENCE":
            noise_count += 1
            continue

        all_evidence: list[Evidence] = []
        for tag in cluster.primary_hashtags[:3]:
            ev = generate_evidence(cluster.contents, "hashtag", tag, f"hashtag_{tag}")
            all_evidence.extend(ev)

        ev_fmt = generate_evidence(cluster.contents, "format", cluster.dominant_format, f"format_{cluster.dominant_format}")
        all_evidence.extend(ev_fmt)

        explanation = _build_explanation(
            cluster, temporal, patterns, score, confidence, lifecycle,
        )

        trend = TrendCandidate(
            id=f"trend_{cluster.id}",
            pattern=cluster.text_signature,
            pattern_type=_primary_pattern_type(patterns),
            lifecycle=lifecycle,
            first_observed_at=temporal.first_seen,
            last_observed_at=temporal.last_seen,
            content_count=content_count,
            unique_creator_count=unique_creators,
            niche_count=niche_count,
            growth_signal=growth_signal,
            engagement_signal=engagement_signal,
            replication_signal=replication_signal,
            cross_niche_signal=cross_niche_signal,
            trend_score=score,
            confidence=confidence,
            evidence=all_evidence[:10],
            contents=[c.content_id for c in cluster.contents],
            primary_hashtags=cluster.primary_hashtags,
            dominant_format=cluster.dominant_format,
            explanation=explanation,
        )
        trend_candidates.append(trend)

    trend_candidates.sort(key=lambda t: t.trend_score, reverse=True)

    return {
        "total_records": len(raw_contents),
        "total_features": len(features),
        "clusters_found": len(all_clusters),
        "trend_candidates": len(trend_candidates),
        "noise_discarded": noise_count,
        "emerging": sum(1 for t in trend_candidates if t.lifecycle == "EMERGING"),
        "growing": sum(1 for t in trend_candidates if t.lifecycle == "GROWING"),
        "viral_single": sum(1 for t in trend_candidates if t.lifecycle == "VIRAL_SINGLE"),
        "candidates": trend_candidates,
    }


def _merge_cluster_results(
    h: ClusterResult,
    t: ClusterResult,
) -> list:
    seen_content_ids: set[str] = set()
    merged = []

    for cluster in h.clusters + t.clusters:
        new_contents = [c for c in cluster.contents if c.content_id not in seen_content_ids]
        if len(new_contents) >= 2:
            seen_content_ids.update(c.content_id for c in new_contents)
            merged.append(cluster)

    merged.sort(key=lambda c: len(c.contents), reverse=True)
    return merged


def _primary_pattern_type(patterns: PatternAnalysis) -> str:
    if patterns.hashtag_patterns:
        return "hashtag"
    if patterns.format_patterns:
        return "format"
    if patterns.structure_patterns:
        return "structure"
    return "generic"


def _build_explanation(
    cluster, temporal, patterns, score, confidence, lifecycle,
) -> str:
    parts = []
    parts.append(f"Cluster with {len(cluster.contents)} contents from {temporal.unique_creators} creators.")

    if temporal.has_temporal_data:
        parts.append(f"Time span: {temporal.span_hours:.1f}h ({temporal.first_seen[:16]} to {temporal.last_seen[:16]}).")

    if cluster.primary_hashtags:
        parts.append(f"Top hashtags: {', '.join('#' + t for t in cluster.primary_hashtags[:3])}.")

    parts.append(f"Format: {cluster.dominant_format}.")

    if patterns.niche_signals:
        parts.append(f"Niches: {', '.join(patterns.niche_signals)}.")

    parts.append(f"Score: {score}, Confidence: {confidence}%, Lifecycle: {lifecycle}.")

    return " ".join(parts)
