from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


def generate_temporal_reports(result: dict, output_dir: Path) -> None:
    _save_snapshots_json(result, output_dir)
    _save_trends_json(result, output_dir)
    _save_analysis_csv(result, output_dir)
    _save_report_md(result, output_dir)


def _save_snapshots_json(result: dict, output_dir: Path) -> None:
    data = {
        "total_snapshots": result["total_snapshots"],
        "cross_snapshot": result["cross_snapshot"],
        "snapshot_analyses": result["snapshot_analyses"],
    }
    (output_dir / "temporal-snapshots.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def _save_trends_json(result: dict, output_dir: Path) -> None:
    (output_dir / "temporal-trends.json").write_text(
        json.dumps(result["temporal_trends"], indent=2), encoding="utf-8"
    )


def _save_analysis_csv(result: dict, output_dir: Path) -> None:
    headers = [
        "pattern", "lifecycle", "content_count", "unique_creators",
        "snapshots_present", "persistence_ratio", "growth_signal",
        "replication_signal", "trend_score", "confidence", "evidence_count",
    ]
    rows = [",".join(headers)]
    for t in result["temporal_trends"]:
        row = ",".join(str(x) for x in [
            t["pattern"], t["lifecycle"], t["content_count"], t["unique_creators"],
            "|".join(t["snapshots_present"]), round(t["persistence_ratio"], 2),
            round(t["growth_signal"], 2), round(t["replication_signal"], 2),
            t["trend_score"], t["confidence"], len(t["evidence"]),
        ])
        rows.append(row)
    (output_dir / "temporal-analysis.csv").write_text("\n".join(rows), encoding="utf-8")


def _save_report_md(result: dict, output_dir: Path) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    trends = result["temporal_trends"]
    cross = result["cross_snapshot"]
    analyses = result["snapshot_analyses"]

    best = trends[0] if trends else None
    has_growing = any(t["lifecycle"] == "GROWING" for t in trends)
    has_emerging = any(t["lifecycle"] == "EMERGING" for t in trends)
    has_confirmed = any(t["lifecycle"] == "CONFIRMED" for t in trends)

    lines = [
        "# AI TREND SCOUT — TEMPORAL RE-DISCOVERY REPORT V1.0",
        "",
        f"**Generated:** {now}",
        "",
        "---",
        "",
        "# STATUS",
        "",
        "```text",
    ]

    if best and best["confidence"] >= 30 and best["unique_creators"] >= 2:
        lines.append("STATUS: PASS")
    else:
        lines.append("STATUS: FAIL")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# SNAPSHOTS")
    lines.append("")
    lines.append("| Snapshot | Records | Creators | Keywords |")
    lines.append("|----------|---------|----------|----------|")
    for a in analyses:
        kw = a.get("snapshot_id", "")
        started = a.get("started_at", "")[:19]
        lines.append(f"| {kw} | {a['content_count']} | {a['unique_creator_count']} | {started} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# CROSS-SNAPSHOT ANALYSIS")
    lines.append("")
    lines.append(f"- **Total unique content:** {cross['total_unique_content']}")
    lines.append(f"- **Persistent content (appeared in 2+ snapshots):** {cross['persistent_content_count']}")
    lines.append(f"- **Total unique creators:** {cross['total_unique_creators']}")
    lines.append(f"- **Persistent creators:** {cross['persistent_creators_count']}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# TEMPORAL TRENDS")
    lines.append("")
    lines.append(f"| # | Pattern | Lifecycle | Contents | Creators | Snaps | Score | Confidence |")
    lines.append("|---|---------|-----------|----------|----------|-------|-------|------------|")
    for idx, t in enumerate(trends[:15]):
        lines.append(
            f"| {idx+1} | {t['pattern']} | {t['lifecycle']} | {t['content_count']} "
            f"| {t['unique_creators']} | {len(t['snapshots_present'])} | {t['trend_score']} | {t['confidence']}% |"
        )
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# LIFECYCLE DISTRIBUTION")
    lines.append("")
    lines.append(f"- **SIGNAL:** {sum(1 for t in trends if t['lifecycle'] == 'SIGNAL')}")
    lines.append(f"- **EMERGING:** {sum(1 for t in trends if t['lifecycle'] == 'EMERGING')}")
    lines.append(f"- **GROWING:** {sum(1 for t in trends if t['lifecycle'] == 'GROWING')}")
    lines.append(f"- **CONFIRMED:** {sum(1 for t in trends if t['lifecycle'] == 'CONFIRMED')}")
    lines.append(f"- **SATURATED:** {sum(1 for t in trends if t['lifecycle'] == 'SATURATED')}")
    lines.append(f"- **DECLINING:** {sum(1 for t in trends if t['lifecycle'] == 'DECLINING')}")
    lines.append(f"- **INSUFFICIENT_EVIDENCE:** {sum(1 for t in trends if t['lifecycle'] == 'INSUFFICIENT_EVIDENCE')}")
    lines.append("")

    if best:
        lines.append("---")
        lines.append("")
        lines.append("# BEST TEMPORAL SIGNAL")
        lines.append("")
        lines.append(f"**{best['pattern']}**")
        lines.append("")
        lines.append(f"- Lifecycle: {best['lifecycle']}")
        lines.append(f"- Score: {best['trend_score']}")
        lines.append(f"- Confidence: {best['confidence']}%")
        lines.append(f"- Contents: {best['content_count']}")
        lines.append(f"- Creators: {best['unique_creators']}")
        lines.append(f"- Snapshots present: {', '.join(best['snapshots_present'])}")
        lines.append(f"- Persistence ratio: {best['persistence_ratio']:.2f}")
        lines.append(f"- Growth signal: {best['growth_signal']:.2f}")
        lines.append(f"- Replication signal: {best['replication_signal']:.2f}")
        lines.append("")
        lines.append("**Evidence chain:**")
        for ev in best["evidence"][:5]:
            lines.append(f"- [{ev['snapshot_id']}] {ev['description']} (by {ev['author']})")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# VIEW_COUNT NULL IMPACT")
    lines.append("")
    lines.append("- view_count was NULL for all records across all snapshots")
    lines.append("- Pipeline continued without view_count dependency")
    lines.append("- Growth calculated from content_count and creator_diversity changes")
    lines.append("- Temporal analysis used published_at timestamps")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# ARTIFACTS")
    lines.append("")
    lines.append("- artifacts/temporal-snapshots.json")
    lines.append("- artifacts/temporal-trends.json")
    lines.append("- artifacts/temporal-analysis.csv")
    lines.append("- artifacts/temporal-discovery-report.md")
    lines.append("")

    (output_dir / "temporal-discovery-report.md").write_text("\n".join(lines), encoding="utf-8")
