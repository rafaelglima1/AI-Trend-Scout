from __future__ import annotations

import json
import sys
from pathlib import Path

from benchmark.trend_detection.pipeline import run_pipeline
from benchmark.trend_detection.reports import generate_reports


ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = ROOT / "artifacts" / "raw-datasets"
ARTIFACTS = ROOT / "artifacts"


def main() -> None:
    print("Phase -1.2: Trend Detection Proof")
    print("=" * 50)

    result = run_pipeline(RAW_DIR)

    print("")
    print("Generating reports...")
    generate_reports(result, ARTIFACTS)

    print("")
    print("=" * 50)
    candidates = result["candidates"]
    best = candidates[0] if candidates else None

    if best:
        print(f"STATUS: PASS")
        print(f"DATASET: {result['total_records']} records")
        print(f"CLUSTERS: {result['clusters_found']}")
        print(f"CANDIDATES: {result['trend_candidates']}")
        print(f"EMERGING: {result['emerging']}")
        print(f"GROWING: {result['growing']}")
        print(f"NOISE: {result['noise_discarded']}")
        print(f"BEST: {best.id}")
        print(f"SCORE: {best.trend_score}")
        print(f"CONFIDENCE: {best.confidence}%")
        print(f"EVIDENCE: {len(best.evidence)}")
        print(f"LIFECYCLE: {best.lifecycle}")
    else:
        print("STATUS: BLOCKER")
        print("No trend candidates found")

    print("=" * 50)


if __name__ == "__main__":
    main()
