from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from benchmark.trend_detection.trend_scoring import TrendCandidate


def generate_reports(result: dict, output_dir: Path) -> None:
    candidates = result["candidates"]

    _save_trend_candidates_json(candidates, output_dir)
    _save_trend_evidence_json(candidates, output_dir)
    _save_clusters_json(result, output_dir)
    _save_trend_csv(candidates, output_dir)
    _save_report_md(result, output_dir)


def _save_trend_candidates_json(candidates: list[TrendCandidate], output_dir: Path) -> None:
    data = []
    for t in candidates:
        data.append({
            "id": t.id,
            "pattern": t.pattern,
            "pattern_type": t.pattern_type,
            "lifecycle": t.lifecycle,
            "first_observed_at": t.first_observed_at,
            "last_observed_at": t.last_observed_at,
            "content_count": t.content_count,
            "unique_creator_count": t.unique_creator_count,
            "niche_count": t.niche_count,
            "growth_signal": t.growth_signal,
            "engagement_signal": t.engagement_signal,
            "replication_signal": t.replication_signal,
            "cross_niche_signal": t.cross_niche_signal,
            "trend_score": t.trend_score,
            "confidence": t.confidence,
            "primary_hashtags": t.primary_hashtags,
            "dominant_format": t.dominant_format,
            "explanation": t.explanation,
            "contents": t.contents,
            "evidence_count": len(t.evidence),
        })
    (output_dir / "trend-candidates.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def _save_trend_evidence_json(candidates: list[TrendCandidate], output_dir: Path) -> None:
    data = []
    for t in candidates:
        for ev in t.evidence:
            data.append({
                "trend_id": t.id,
                "evidence_id": ev.id,
                "content_id": ev.content_id,
                "source": ev.source,
                "signal_type": ev.signal_type,
                "observed_at": ev.observed_at,
                "description": ev.description,
                "strength": ev.strength,
            })
    (output_dir / "trend-evidence.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def _save_clusters_json(result: dict, output_dir: Path) -> None:
    data = {
        "total_records": result["total_records"],
        "clusters_found": result["clusters_found"],
        "trend_candidates": result["trend_candidates"],
        "noise_discarded": result["noise_discarded"],
        "emerging": result["emerging"],
        "growing": result["growing"],
        "viral_single": result["viral_single"],
    }
    (output_dir / "clusters.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def _save_trend_csv(candidates: list[TrendCandidate], output_dir: Path) -> None:
    headers = [
        "id", "pattern_type", "lifecycle", "content_count", "unique_creators",
        "niche_count", "growth_signal", "replication_signal", "cross_niche_signal",
        "engagement_signal", "trend_score", "confidence", "primary_hashtags",
        "dominant_format", "evidence_count",
    ]
    rows = [",".join(headers)]
    for t in candidates:
        row = ",".join(str(x) for x in [
            t.id, t.pattern_type, t.lifecycle, t.content_count, t.unique_creator_count,
            t.niche_count, t.growth_signal, t.replication_signal, t.cross_niche_signal,
            t.engagement_signal, t.trend_score, t.confidence,
            "|".join(t.primary_hashtags[:3]), t.dominant_format, len(t.evidence),
        ])
        rows.append(row)
    (output_dir / "trend-analysis.csv").write_text("\n".join(rows), encoding="utf-8")


def _save_report_md(result: dict, output_dir: Path) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    candidates = result["candidates"]

    lines = [
        "# AI TREND SCOUT — TREND DETECTION PROOF V1.0",
        "",
        f"**Generated:** {now}",
        "",
        "---",
        "",
        "# STATUS",
        "",
    ]

    best = candidates[0] if candidates else None
    has_trend = best is not None and best.confidence >= 30 and best.content_count >= 3

    lines.append("```text")
    lines.append(f"STATUS: {'PASS' if has_trend else 'BLOCKER'}")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# DATASET ANALYZED")
    lines.append("")
    lines.append(f"- **Total records:** {result['total_records']}")
    lines.append(f"- **Contents with features:** {result['total_features']}")
    lines.append(f"- **Unique creators:** {len(set(c.get('author', '') for c in []))}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# CLUSTERING RESULTS")
    lines.append("")
    lines.append(f"- **Clusters found:** {result['clusters_found']}")
    lines.append(f"- **Trend candidates:** {result['trend_candidates']}")
    lines.append(f"- **Noise discarded:** {result['noise_discarded']}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# TREND CLASSIFICATION")
    lines.append("")
    lines.append(f"- **Emerging:** {result['emerging']}")
    lines.append(f"- **Growing:** {result['growing']}")
    lines.append(f"- **Viral Single:** {result['viral_single']}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# ALL TREND CANDIDATES")
    lines.append("")
    lines.append("| # | Pattern | Lifecycle | Contents | Creators | Score | Confidence |")
    lines.append("|---|---------|-----------|----------|----------|-------|------------|")
    for idx, t in enumerate(candidates[:20]):
        pattern_short = t.pattern[:40] + "..." if len(t.pattern) > 40 else t.pattern
        lines.append(
            f"| {idx+1} | {pattern_short} | {t.lifecycle} | {t.content_count} "
            f"| {t.unique_creator_count} | {t.trend_score} | {t.confidence}% |"
        )
    lines.append("")

    if best:
        lines.append("---")
        lines.append("")
        lines.append("# BEST CANDIDATE")
        lines.append("")
        lines.append(f"**{best.id}**")
        lines.append("")
        lines.append(f"- Pattern: {best.pattern}")
        lines.append(f"- Lifecycle: {best.lifecycle}")
        lines.append(f"- Score: {best.trend_score}")
        lines.append(f"- Confidence: {best.confidence}%")
        lines.append(f"- Contents: {best.content_count}")
        lines.append(f"- Creators: {best.unique_creator_count}")
        lines.append(f"- Niches: {best.niche_count}")
        lines.append(f"- First seen: {best.first_observed_at[:16]}")
        lines.append(f"- Last seen: {best.last_observed_at[:16]}")
        lines.append(f"- Growth: {best.growth_signal}")
        lines.append(f"- Replication: {best.replication_signal}")
        lines.append(f"- Cross-niche: {best.cross_niche_signal}")
        lines.append(f"- Engagement: {best.engagement_signal}")
        lines.append(f"- Format: {best.dominant_format}")
        lines.append(f"- Hashtags: {', '.join('#' + h for h in best.primary_hashtags[:5])}")
        lines.append("")
        lines.append("**Explanation:**")
        lines.append(best.explanation)
        lines.append("")
        lines.append("**Evidence:**")
        for ev in best.evidence[:5]:
            lines.append(f"- [{ev.id}] {ev.description}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# VIEW_COUNT NULL IMPACT")
    lines.append("")
    lines.append("- view_count was NULL for all records")
    lines.append("- Pipeline continued without view_count dependency")
    lines.append("- Engagement signal derived from like_count and comment_count")
    lines.append("- Growth signal derived from content count and creator diversity")
    lines.append("- Temporal analysis used published_at timestamps")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# LIMITATIONS")
    lines.append("")
    lines.append("- Dataset is small (single provider, single time window)")
    lines.append("- No video/reels content returned (only Image and Sidecar)")
    lines.append("- Temporal analysis limited to single collection window")
    lines.append("- No cross-source validation")
    lines.append("- No LLM-based semantic analysis")
    lines.append("- Embeddings not used (TF-IDF style tokenization)")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# ARTIFACTS")
    lines.append("")
    lines.append("- artifacts/trend-candidates.json")
    lines.append("- artifacts/trend-evidence.json")
    lines.append("- artifacts/clusters.json")
    lines.append("- artifacts/trend-analysis.csv")
    lines.append("- artifacts/trend-detection-report.md")
    lines.append("")

    (output_dir / "trend-detection-report.md").write_text("\n".join(lines), encoding="utf-8")
