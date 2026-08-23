from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

from benchmark.trend_detection.content_intelligence import extract_features, ContentFeatures
from benchmark.trend_detection.clustering import cluster_by_hashtag_similarity
from benchmark.trend_detection.temporal import compute_temporal_signal
from benchmark.trend_detection.pattern_detection import detect_patterns
from benchmark.trend_detection.trend_scoring import compute_trend_score, determine_lifecycle


def load_snapshots(snapshots_dir: Path) -> list[dict]:
    snapshots = []
    for f in sorted(snapshots_dir.glob("snapshot_T*.json")):
        snapshots.append(json.loads(f.read_text(encoding="utf-8")))
    return snapshots


def analyze_temporal(snapshots: list[dict]) -> dict:
    snapshot_analyses = []

    for snap in snapshots:
        contents = snap.get("contents", [])
        features = [extract_features(c) for c in contents]

        cluster_result = cluster_by_hashtag_similarity(features, min_overlap=2)
        temporal = compute_temporal_signal(features)

        snapshot_analyses.append({
            "snapshot_id": snap["snapshot_id"],
            "started_at": snap["started_at"],
            "content_count": snap["content_count"],
            "unique_creator_count": snap["unique_creator_count"],
            "clusters": [
                {
                    "id": cl.id,
                    "content_count": len(cl.contents),
                    "creator_count": len(set(c.author for c in cl.contents)),
                    "primary_hashtags": cl.primary_hashtags,
                    "dominant_format": cl.dominant_format,
                    "content_ids": [c.content_id for c in cl.contents],
                    "creators": list(set(c.author for c in cl.contents)),
                }
                for cl in cluster_result.clusters
            ],
            "noise_count": len(cluster_result.noise),
        })

    cross_snapshot = _cross_snapshot_analysis(snapshots)

    temporal_trends = _detect_temporal_trends(snapshots, snapshot_analyses, cross_snapshot)

    return {
        "total_snapshots": len(snapshots),
        "snapshot_analyses": snapshot_analyses,
        "cross_snapshot": cross_snapshot,
        "temporal_trends": temporal_trends,
    }


def _cross_snapshot_analysis(snapshots: list[dict]) -> dict:
    all_ids: dict[str, set[str]] = {}
    all_authors: dict[str, set[str]] = {}
    all_hashtags: dict[str, Counter] = {}

    for snap in snapshots:
        sid = snap["snapshot_id"]
        ids = set()
        authors = set()
        hashtags = Counter()

        for c in snap.get("contents", []):
            eid = c.get("external_id", "")
            if eid:
                ids.add(eid)
                all_ids.setdefault(eid, set()).add(sid)

            author = c.get("author", "unknown")
            if author != "unknown":
                authors.add(author)
                all_authors.setdefault(author, set()).add(sid)

            for h in c.get("hashtags", []):
                hashtags[h] += 1
                all_hashtags.setdefault(h, Counter())[sid] += 1

    persistent_content = {eid: snaps for eid, snaps in all_ids.items() if len(snaps) >= 2}
    persistent_creators = {a: snaps for a, snaps in all_authors.items() if len(snaps) >= 2}

    persistent_hashtags = {}
    for tag, snap_counts in all_hashtags.items():
        if len(snap_counts) >= 2:
            persistent_hashtags[tag] = snap_counts

    return {
        "total_unique_content": len(all_ids),
        "persistent_content_count": len(persistent_content),
        "persistent_content": {eid: sorted(list(snaps)) for eid, snaps in list(persistent_content.items())[:20]},
        "total_unique_creators": len(all_authors),
        "persistent_creators_count": len(persistent_creators),
        "persistent_creators": {a: sorted(list(snaps)) for a, snaps in list(persistent_creators.items())[:20]},
        "persistent_hashtags": {tag: dict(counts) for tag, counts in list(persistent_hashtags.items())[:20]},
    }


def _detect_temporal_trends(
    snapshots: list[dict],
    analyses: list[dict],
    cross_snapshot: dict,
) -> list[dict]:
    trends = []

    for tag, snap_counts in cross_snapshot.get("persistent_hashtags", {}).items():
        content_creators: dict[str, set[str]] = {}
        content_snapshots: dict[str, set[str]] = {}

        for snap in snapshots:
            sid = snap["snapshot_id"]
            for c in snap.get("contents", []):
                if tag in c.get("hashtags", []):
                    eid = c.get("external_id", "")
                    author = c.get("author", "unknown")
                    if eid:
                        content_creators.setdefault(tag, set()).add(author)
                        content_snapshots.setdefault(tag, set()).add(sid)

        tag_creators = content_creators.get(tag, set())
        tag_snaps = content_snapshots.get(tag, set())

        if len(tag_creators) < 2 or len(tag_snaps) < 2:
            continue

        content_count = sum(snap_counts.values())
        creator_count = len(tag_creators)
        snap_count = len(tag_snaps)

        growth_signal = min(1.0, (snap_count / len(snapshots)) * (content_count / 10.0))
        replication_signal = min(1.0, creator_count / 5.0)

        score, confidence = compute_trend_score(
            temporal=None,
            content_count=content_count,
            unique_creators=creator_count,
            niche_count=1,
            has_engagement=False,
            has_temporal_data=True,
        )

        lifecycle = determine_lifecycle(
            content_count=content_count,
            unique_creators=creator_count,
            growth_signal=growth_signal,
            confidence=confidence,
            temporal=None,
        )

        evidence = []
        for snap in snapshots:
            sid = snap["snapshot_id"]
            for c in snap.get("contents", []):
                if tag in c.get("hashtags", []):
                    evidence.append({
                        "snapshot_id": sid,
                        "content_id": c.get("external_id", ""),
                        "author": c.get("author", "unknown"),
                        "observed_at": c.get("published_at", ""),
                        "description": f"Content with #{tag} in snapshot {sid}",
                    })

        trends.append({
            "pattern": f"#{tag}",
            "pattern_type": "hashtag",
            "content_count": content_count,
            "unique_creators": creator_count,
            "snapshots_present": sorted(list(tag_snaps)),
            "persistence_ratio": snap_count / len(snapshots),
            "growth_signal": growth_signal,
            "replication_signal": replication_signal,
            "trend_score": score,
            "confidence": confidence,
            "lifecycle": lifecycle,
            "evidence": evidence[:15],
        })

    trends.sort(key=lambda t: t["trend_score"], reverse=True)
    return trends
