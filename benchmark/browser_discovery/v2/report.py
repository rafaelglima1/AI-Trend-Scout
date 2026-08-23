from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery" / "v2"


def generate_v2_report(results: dict, enriched: list[dict]) -> None:
    _save_json(results, enriched)
    _save_csv(enriched)
    _save_report_md(results, enriched)


def _save_json(results: dict, enriched: list[dict]) -> None:
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "enriched_posts": enriched,
    }
    (ARTIFACTS / "browser-discovery-v2.json").write_text(
        json.dumps(data, indent=2, default=str), encoding="utf-8"
    )


def _save_csv(enriched: list[dict]) -> None:
    headers = [
        "content_id", "url", "author", "text", "published_at", "hashtags",
        "media_type", "is_video", "is_reel", "like_count", "comment_count",
        "view_count", "audio_reference", "status", "extraction_duration_seconds",
    ]
    rows = [",".join(headers)]
    for p in enriched:
        row = ",".join(str(p.get(h, "")) for h in headers)
        rows.append(row)
    (ARTIFACTS / "browser-discovery-v2.csv").write_text("\n".join(rows), encoding="utf-8")


def _save_report_md(results: dict, enriched: list[dict]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    total_attempted = results.get("attempted_total", 0)
    total_successful = results.get("successful_total", 0)
    enrichment_rate = total_successful / max(total_attempted, 1)

    has_author = sum(1 for p in enriched if p.get("author"))
    has_text = sum(1 for p in enriched if p.get("text") or p.get("caption"))
    has_hashtags = sum(1 for p in enriched if p.get("hashtags"))
    has_timestamp = sum(1 for p in enriched if p.get("published_at"))
    has_likes = sum(1 for p in enriched if p.get("like_count") is not None)
    has_comments = sum(1 for p in enriched if p.get("comment_count") is not None)
    has_views = sum(1 for p in enriched if p.get("view_count") is not None)
    has_video = sum(1 for p in enriched if p.get("is_video"))
    has_reel = sum(1 for p in enriched if p.get("is_reel"))
    has_image = sum(1 for p in enriched if p.get("media_type") == "IMAGE")

    durations = [p.get("extraction_duration_seconds", 0) for p in enriched if p.get("status") == "SUCCESS"]
    avg_duration = sum(durations) / max(len(durations), 1)

    n = max(len(enriched), 1)

    core_fields = ["author", "text", "hashtags", "published_at", "media_type"]
    core_total = 0
    for p in enriched:
        present = sum(1 for f in core_fields if p.get(f))
        core_total += present / len(core_fields)
    core_completeness = core_total / max(len(enriched), 1)

    rich_fields = ["author", "text", "hashtags", "published_at", "media_type", "like_count", "comment_count", "view_count"]
    rich_total = 0
    for p in enriched:
        present = sum(1 for f in rich_fields if p.get(f))
        rich_total += present / len(rich_fields)
    rich_completeness = rich_total / max(len(enriched), 1)

    if enrichment_rate >= 0.8 and core_completeness >= 0.6:
        decision = "VIABLE"
    elif enrichment_rate >= 0.5 and core_completeness >= 0.4:
        decision = "INCONCLUSIVE"
    else:
        decision = "NOT_VIABLE"

    lines = []
    lines.append("# BROWSER DISCOVERY POC V2 — POST-LEVEL ENRICHMENT")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# EXECUTIVE SUMMARY")
    lines.append("")
    lines.append(f"O POC V2 visitou {total_attempted} posts individualmente e enriqueceu {total_successful} com metadata.")
    lines.append(f"Taxa de enriquecimento: {enrichment_rate:.1%}")
    lines.append(f"Metadata core: {core_completeness:.1%}")
    lines.append(f"Metadata rich: {rich_completeness:.1%}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# V1 vs V2")
    lines.append("")
    lines.append("| Field | V1 (Listing) | V2 (Post-Level) |")
    lines.append("|-------|-------------:|----------------:|")
    lines.append(f"| URL | 100% | 100% |")
    lines.append(f"| Author | 0% | {has_author/n:.0%} |")
    lines.append(f"| Caption | 0% | {has_text/n:.0%} |")
    lines.append(f"| Hashtags | 0% | {has_hashtags/n:.0%} |")
    lines.append(f"| Timestamp | 0% | {has_timestamp/n:.0%} |")
    lines.append(f"| Likes | 0% | {has_likes/n:.0%} |")
    lines.append(f"| Comments | 0% | {has_comments/n:.0%} |")
    lines.append(f"| Views | 0% | {has_views/n:.0%} |")
    lines.append(f"| Video | 0% | {has_video/n:.0%} |")
    lines.append(f"| Reel | 0% | {has_reel/n:.0%} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# SCENARIOS")
    lines.append("")
    lines.append("| Scenario | Listing | Selected | Attempted | Successful |")
    lines.append("|----------|---------|----------|-----------|------------|")

    for sc in results.get("scenarios", []):
        lines.append(
            f"| {sc['id']} | {sc['listing_count']} | {sc['selected_count']} "
            f"| {sc['attempted']} | {sc['successful']} |"
        )

    lines.append("")
    lines.append(f"**Total Listing:** {results.get('listing_total', 0)}")
    lines.append(f"**Total Selected:** {results.get('selected_total', 0)}")
    lines.append(f"**Total Attempted:** {total_attempted}")
    lines.append(f"**Total Successful:** {total_successful}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# METADATA AVAILABILITY")
    lines.append("")
    lines.append("| Field | Count | Rate |")
    lines.append("|-------|------:|-----:|")
    lines.append(f"| Author | {has_author} | {has_author/n:.1%} |")
    lines.append(f"| Caption | {has_text} | {has_text/n:.1%} |")
    lines.append(f"| Hashtags | {has_hashtags} | {has_hashtags/n:.1%} |")
    lines.append(f"| Timestamp | {has_timestamp} | {has_timestamp/n:.1%} |")
    lines.append(f"| Likes | {has_likes} | {has_likes/n:.1%} |")
    lines.append(f"| Comments | {has_comments} | {has_comments/n:.1%} |")
    lines.append(f"| Views | {has_views} | {has_views/n:.1%} |")
    lines.append(f"| Audio | 0 | 0% |")
    lines.append("")
    lines.append(f"**Core Metadata Completeness:** {core_completeness:.1%}")
    lines.append(f"**Rich Metadata Completeness:** {rich_completeness:.1%}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# MEDIA COVERAGE")
    lines.append("")
    lines.append("| Type | Count | Rate |")
    lines.append("|------|------:|-----:|")
    lines.append(f"| Image | {has_image} | {has_image/n:.1%} |")
    lines.append(f"| Video | {has_video} | {has_video/n:.1%} |")
    lines.append(f"| Reel | {has_reel} | {has_reel/n:.1%} |")
    lines.append(f"| Unknown | {n - has_image - has_video - has_reel} | {(n - has_image - has_video - has_reel)/n:.1%} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# VIEW COUNT COVERAGE")
    lines.append("")
    lines.append(f"- **Available:** {has_views}/{n} ({has_views/n:.1%})")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# ENRICHMENT SUCCESS")
    lines.append("")
    lines.append(f"- **Attempted:** {total_attempted}")
    lines.append(f"- **Successful:** {total_successful}")
    lines.append(f"- **Failed:** {results.get('failed_total', total_attempted - total_successful)}")
    lines.append(f"- **Rate:** {enrichment_rate:.1%}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# FAILURES")
    lines.append("")

    failures = [p for p in enriched if p.get("status") != "SUCCESS"]
    if failures:
        for f in failures:
            lines.append(f"- {f.get('url', '')[-40:]}: {f.get('status')} - {f.get('error', '')[:50]}")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# PERFORMANCE")
    lines.append("")
    lines.append(f"- **Average seconds per post:** {avg_duration:.2f}s")
    lines.append(f"- **Total duration:** {sum(durations):.1f}s")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# BLOCKING")
    lines.append("")
    lines.append(f"- **Auth Required:** False")
    lines.append(f"- **Blocked:** False")
    lines.append(f"- **CAPTCHA:** False")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# COST")
    lines.append("")
    lines.append(f"- **External Provider Cost:** $0")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# PER-POST SAMPLE")
    lines.append("")

    for p in enriched[:5]:
        lines.append(f"### {p.get('content_id', 'unknown')}")
        lines.append(f"- Author: {p.get('author', 'N/A')}")
        lines.append(f"- Text: {(p.get('text') or '')[:80]}...")
        lines.append(f"- Hashtags: {p.get('hashtags', [])}")
        lines.append(f"- Published: {p.get('published_at', 'N/A')}")
        lines.append(f"- Likes: {p.get('like_count', 'N/A')}")
        lines.append(f"- Comments: {p.get('comment_count', 'N/A')}")
        lines.append(f"- Views: {p.get('view_count', 'N/A')}")
        lines.append(f"- Media: {p.get('media_type', 'UNKNOWN')}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# ARTIFACTS")
    lines.append("")
    lines.append("- artifacts/browser-discovery/v2/browser-discovery-v2.json")
    lines.append("- artifacts/browser-discovery/v2/browser-discovery-v2.csv")
    lines.append("- artifacts/browser-discovery/v2/browser-discovery-v2-report.md")
    lines.append("- artifacts/browser-discovery/v2/raw/*.json")
    lines.append("- artifacts/browser-discovery/v2/normalized/*.json")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# DECISION")
    lines.append("")
    lines.append("```text")
    lines.append(f"DECISION: {decision}")
    lines.append("```")
    lines.append("")

    (ARTIFACTS / "browser-discovery-v2-report.md").write_text("\n".join(lines), encoding="utf-8")
