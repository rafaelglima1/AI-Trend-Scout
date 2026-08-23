from __future__ import annotations

import json
from pathlib import Path

from benchmark.trend_detection.temporal_analysis import load_snapshots, analyze_temporal
from benchmark.trend_detection.temporal_reports import generate_temporal_reports


ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOTS_DIR = ROOT / "artifacts" / "temporal-snapshots"
ARTIFACTS = ROOT / "artifacts"


def main() -> None:
    print("Phase -1.3: Temporal Re-Discovery Analysis")
    print("=" * 50)

    snapshots = load_snapshots(SNAPSHOTS_DIR)
    print(f"Loaded {len(snapshots)} snapshots")

    for snap in snapshots:
        print(f"  {snap['snapshot_id']}: {snap['content_count']} records, {snap['unique_creator_count']} creators")

    result = analyze_temporal(snapshots)

    print("")
    print("Generating reports...")
    generate_temporal_reports(result, ARTIFACTS)

    trends = result["temporal_trends"]
    cross = result["cross_snapshot"]

    print("")
    print("=" * 50)
    print(f"Total unique content: {cross['total_unique_content']}")
    print(f"Persistent content: {cross['persistent_content_count']}")
    print(f"Persistent creators: {cross['persistent_creators_count']}")
    print(f"Temporal trends found: {len(trends)}")

    lifecycle_counts = {}
    for t in trends:
        lc = t["lifecycle"]
        lifecycle_counts[lc] = lifecycle_counts.get(lc, 0) + 1
    for lc, count in sorted(lifecycle_counts.items()):
        print(f"  {lc}: {count}")

    if trends:
        best = trends[0]
        print(f"\nBest signal: {best['pattern']}")
        print(f"  Lifecycle: {best['lifecycle']}")
        print(f"  Score: {best['trend_score']}")
        print(f"  Confidence: {best['confidence']}%")
        print(f"  Creators: {best['unique_creators']}")
        print(f"  Snapshots: {best['snapshots_present']}")
        print(f"  Persistence: {best['persistence_ratio']:.2f}")

    print("=" * 50)


if __name__ == "__main__":
    main()
