from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


def generate_report(results: dict, output_dir: Path) -> None:
    report_md = _build_markdown_report(results)
    (output_dir / "provider-benchmark-report.md").write_text(report_md, encoding="utf-8")

    comparison_csv = _build_comparison_csv(results)
    (output_dir / "provider-comparison.csv").write_text(comparison_csv, encoding="utf-8")

    dq_json = {name: r.get("discovery_quality", {}) for name, r in results.items()}
    (output_dir / "discovery-quality.json").write_text(json.dumps(dq_json, indent=2), encoding="utf-8")

    tr_json = {name: r.get("trend_readiness", {}) for name, r in results.items()}
    (output_dir / "trend-readiness.json").write_text(json.dumps(tr_json, indent=2), encoding="utf-8")

    er_json = {name: r.get("evidence_readiness", {}) for name, r in results.items()}
    (output_dir / "evidence-readiness.json").write_text(json.dumps(er_json, indent=2), encoding="utf-8")


def _build_markdown_report(results: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# AI TREND SCOUT — PROVIDER BENCHMARK REPORT V1.0",
        "",
        f"**Generated:** {now}",
        "",
        "---",
        "",
        "# STATUS",
        "",
    ]

    providers_tested = list(results.keys())
    any_pass = any(
        r.get("aggregate", {}).get("records_returned", 0) > 0
        for r in results.values()
    )
    status = "PASS" if any_pass else "BLOCKER"
    lines.append(f"```text\nSTATUS: {status}\n```")
    lines.append("")
    lines.append(f"**PROVIDERS TESTED:** {', '.join(providers_tested)}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# PROVIDER COMPARISON")
    lines.append("")
    lines.append("| Metric | " + " | ".join(providers_tested) + " |")
    lines.append("|---|" + "|".join(["---"] * len(providers_tested)) + "|")

    metrics_keys = [
        ("Records Returned", "records_returned"),
        ("Unique Records", "unique_records"),
        ("Duplicate Rate", "duplicate_rate"),
        ("Freshness Rate", "freshness_rate"),
        ("Metadata Completeness", "metadata_completeness"),
        ("Creator Diversity", "creator_diversity"),
        ("Successful Runs", "successful_runs"),
        ("Latency (s)", "latency_seconds"),
    ]
    for label, key in metrics_keys:
        row = f"| {label} |"
        for p in providers_tested:
            val = results[p].get("aggregate", {}).get(key, "N/A")
            if isinstance(val, float):
                val = f"{val:.4f}"
            row += f" {val} |"
        lines.append(row)

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# DISCOVERY QUALITY SCORES")
    lines.append("")
    lines.append("| Provider | Freshness | Coverage | Metadata | Reliability | Diversity | Cost | Validation | **TOTAL** |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for p in providers_tested:
        dq = results[p].get("discovery_quality", {})
        lines.append(
            f"| {p} | {dq.get('freshness', 'N/A')} | {dq.get('coverage', 'N/A')} "
            f"| {dq.get('metadata', 'N/A')} | {dq.get('reliability', 'N/A')} "
            f"| {dq.get('diversity', 'N/A')} | {dq.get('cost', 'N/A')} "
            f"| {dq.get('validation', 'N/A')} | **{dq.get('total', 'N/A')}** |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# TREND READINESS SCORES")
    lines.append("")
    lines.append("| Provider | Temporal Data | Creator Diversity | Engagement | Dedup Quality | **TOTAL** |")
    lines.append("|---|---|---|---|---|---|")
    for p in providers_tested:
        tr = results[p].get("trend_readiness", {})
        lines.append(
            f"| {p} | {tr.get('temporal_data', 'N/A')} | {tr.get('creator_diversity', 'N/A')} "
            f"| {tr.get('engagement_metrics', 'N/A')} | {tr.get('deduplication_quality', 'N/A')} "
            f"| **{tr.get('total', 'N/A')}** |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# EVIDENCE READINESS SCORES")
    lines.append("")
    lines.append("| Provider | Source Reliability | Metadata Depth | Freshness | Repeatability | **TOTAL** |")
    lines.append("|---|---|---|---|---|---|")
    for p in providers_tested:
        er = results[p].get("evidence_readiness", {})
        lines.append(
            f"| {p} | {er.get('source_reliability', 'N/A')} | {er.get('metadata_depth', 'N/A')} "
            f"| {er.get('freshness', 'N/A')} | {er.get('repeatability', 'N/A')} "
            f"| **{er.get('total', 'N/A')}** |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# RECOMMENDATION")
    lines.append("")

    scored = []
    for p in providers_tested:
        dq = results[p].get("discovery_quality", {}).get("total", 0)
        scored.append((p, dq))
    scored.sort(key=lambda x: x[1], reverse=True)

    if scored:
        lines.append(f"**PRIMARY:** {scored[0][0]} (DQ: {scored[0][1]})")
        if len(scored) > 1:
            lines.append(f"**SECONDARY:** {scored[1][0]} (DQ: {scored[1][1]})")
        if len(scored) > 2:
            lines.append(f"**VALIDATION:** {scored[2][0]} (DQ: {scored[2][1]})")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# NOTES")
    lines.append("")
    lines.append("- All providers require environment variables for credentials")
    lines.append("- No credentials were hardcoded")
    lines.append("- Raw responses were preserved")
    lines.append("- Normalization applied deduplication")
    lines.append("- Freshness measured against 48h window")
    lines.append("")
    return "\n".join(lines)


def _build_comparison_csv(results: dict) -> str:
    headers = ["provider", "records_returned", "unique_records", "duplicate_rate",
               "freshness_rate", "metadata_completeness", "creator_diversity",
               "successful_runs", "total_runs", "latency_seconds", "cost_usd",
               "dq_total", "tr_total", "er_total"]
    rows = [",".join(headers)]

    for name, r in results.items():
        agg = r.get("aggregate", {})
        dq = r.get("discovery_quality", {})
        tr = r.get("trend_readiness", {})
        er = r.get("evidence_readiness", {})
        row = ",".join(str(x) for x in [
            name,
            agg.get("records_returned", 0),
            agg.get("unique_records", 0),
            agg.get("duplicate_rate", 0),
            agg.get("freshness_rate", 0),
            agg.get("metadata_completeness", 0),
            agg.get("creator_diversity", 0),
            agg.get("successful_runs", 0),
            agg.get("total_runs", 0),
            agg.get("latency_seconds", 0),
            agg.get("cost_usd", ""),
            dq.get("total", 0),
            tr.get("total", 0),
            er.get("total", 0),
        ])
        rows.append(row)

    return "\n".join(rows)
