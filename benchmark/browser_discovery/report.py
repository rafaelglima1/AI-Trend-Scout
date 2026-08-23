from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from benchmark.browser_discovery.metrics import BrowserMetrics


def generate_report(
    metrics: BrowserMetrics,
    scenario_results: list[dict],
    raw_contents: dict[str, list[dict]],
    normalized_contents: dict[str, list[dict]],
    output_dir: Path,
) -> None:
    _save_json(metrics, scenario_results, output_dir)
    _save_csv(metrics, output_dir)
    _save_report_md(metrics, scenario_results, output_dir)


def _save_json(metrics: BrowserMetrics, scenario_results: list[dict], output_dir: Path) -> None:
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "records_returned": metrics.records_returned,
            "unique_records": metrics.unique_records,
            "unique_creators": metrics.unique_creators,
            "duplicate_rate": metrics.duplicate_rate,
            "freshness_rate": metrics.freshness_rate,
            "metadata_completeness": metrics.metadata_completeness,
            "creator_diversity": metrics.creator_diversity,
            "timestamp_availability": metrics.timestamp_availability,
            "hashtag_availability": metrics.hashtag_availability,
            "author_availability": metrics.author_availability,
            "text_availability": metrics.text_availability,
            "like_count_availability": metrics.like_count_availability,
            "comment_count_availability": metrics.comment_count_availability,
            "view_count_availability": metrics.view_count_availability,
            "video_rate": metrics.video_rate,
            "reel_rate": metrics.reel_rate,
            "scenario_success_rate": metrics.scenario_success_rate,
            "browser_duration_seconds": metrics.browser_duration_seconds,
            "blocked": metrics.blocked,
            "auth_required": metrics.auth_required,
            "captcha": metrics.captcha,
        },
        "scenarios": scenario_results,
    }
    (output_dir / "browser-discovery.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def _save_csv(metrics: BrowserMetrics, output_dir: Path) -> None:
    headers = [
        "metric", "value",
    ]
    rows = [",".join(headers)]
    data = [
        ("records_returned", metrics.records_returned),
        ("unique_records", metrics.unique_records),
        ("unique_creators", metrics.unique_creators),
        ("duplicate_rate", metrics.duplicate_rate),
        ("freshness_rate", metrics.freshness_rate or "N/A"),
        ("metadata_completeness", round(metrics.metadata_completeness, 4)),
        ("creator_diversity", round(metrics.creator_diversity, 4)),
        ("timestamp_availability", round(metrics.timestamp_availability, 4)),
        ("hashtag_availability", round(metrics.hashtag_availability, 4)),
        ("author_availability", round(metrics.author_availability, 4)),
        ("text_availability", round(metrics.text_availability, 4)),
        ("like_count_availability", round(metrics.like_count_availability, 4)),
        ("comment_count_availability", round(metrics.comment_count_availability, 4)),
        ("view_count_availability", round(metrics.view_count_availability, 4)),
        ("video_rate", round(metrics.video_rate, 4)),
        ("reel_rate", round(metrics.reel_rate, 4)),
        ("scenario_success_rate", round(metrics.scenario_success_rate, 4)),
        ("browser_duration_seconds", round(metrics.browser_duration_seconds, 2)),
        ("blocked", metrics.blocked),
        ("auth_required", metrics.auth_required),
        ("captcha", metrics.captcha),
    ]
    for k, v in data:
        rows.append(f"{k},{v}")
    (output_dir / "browser-discovery.csv").write_text("\n".join(rows), encoding="utf-8")


def _save_report_md(metrics: BrowserMetrics, scenario_results: list[dict], output_dir: Path) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if metrics.auth_required:
        status = "BLOCKER"
    elif metrics.records_returned > 0:
        status = "PASS"
    else:
        status = "FAIL"

    lines = [
        "# BROWSER DISCOVERY POC",
        "",
        f"**Generated:** {now}",
        "",
        "---",
        "",
        "# STATUS",
        "",
        "```text",
        f"STATUS: {status}",
        "```",
        "",
        "---",
        "",
        "# SCENARIOS",
        "",
        "| # | Scenario | URL | Status | Records |",
        "|---|----------|-----|--------|---------|",
    ]

    for idx, sr in enumerate(scenario_results):
        lines.append(
            f"| {idx+1} | {sr['id']} | {sr['url'][:40]}... | {sr['status']} | {sr['records']} |"
        )
    lines.append("")

    lines.extend([
        "---",
        "",
        "# DATASET",
        "",
        f"- **Total records:** {metrics.records_returned}",
        f"- **Unique records:** {metrics.unique_records}",
        f"- **Unique creators:** {metrics.unique_creators}",
        f"- **Duplicate rate:** {metrics.duplicate_rate:.4f}",
        "",
        "---",
        "",
        "# METRICS",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Freshness | {metrics.freshness_rate:.4f} |" if metrics.freshness_rate else "| Freshness | N/A |",
        f"| Metadata Completeness | {metrics.metadata_completeness:.4f} |",
        f"| Creator Diversity | {metrics.creator_diversity:.4f} |",
        f"| Timestamp Availability | {metrics.timestamp_availability:.4f} |",
        f"| Hashtag Availability | {metrics.hashtag_availability:.4f} |",
        f"| Author Availability | {metrics.author_availability:.4f} |",
        f"| Text Availability | {metrics.text_availability:.4f} |",
        f"| Like Count Availability | {metrics.like_count_availability:.4f} |",
        f"| Comment Count Availability | {metrics.comment_count_availability:.4f} |",
        f"| View Count Availability | {metrics.view_count_availability:.4f} |",
        f"| Video Rate | {metrics.video_rate:.4f} |",
        f"| Reel Rate | {metrics.reel_rate:.4f} |",
        f"| Scenario Success Rate | {metrics.scenario_success_rate:.4f} |",
        f"| Browser Duration | {metrics.browser_duration_seconds:.2f}s |",
        "",
        "---",
        "",
        "# BLOCKING CONDITIONS",
        "",
        f"- **Auth Required:** {metrics.auth_required}",
        f"- **Blocked:** {metrics.blocked}",
        f"- **CAPTCHA:** {metrics.captcha}",
        "",
        "---",
        "",
        "# ERRORS",
        "",
    ])

    for sr in scenario_results:
        if sr.get("error"):
            lines.append(f"- **{sr['id']}:** {sr['error']}")

    if not any(sr.get("error") for sr in scenario_results):
        lines.append("- None")

    lines.extend([
        "",
        "---",
        "",
        "# ARTIFACTS",
        "",
        "- artifacts/browser-discovery/browser-discovery.json",
        "- artifacts/browser-discovery/browser-discovery.csv",
        "- artifacts/browser-discovery/browser-discovery-report.md",
        "- artifacts/browser-discovery/raw/*.json",
        "- artifacts/browser-discovery/normalized/*.json",
        "",
    ])

    (output_dir / "browser-discovery-report.md").write_text("\n".join(lines), encoding="utf-8")
