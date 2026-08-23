from __future__ import annotations

import asyncio
import json
from pathlib import Path

from benchmark.providers.meta_official import MetaOfficialProvider
from benchmark.providers.bright_data import BrightDataProvider
from benchmark.providers.apify import ApifyProvider
from benchmark.runner.scenarios import SCENARIOS
from benchmark.normalization import normalize
from benchmark.metrics import (
    compute_metrics, aggregate_metrics,
    compute_discovery_quality, compute_trend_readiness, compute_evidence_readiness,
)
from benchmark.reports import generate_report

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
(ARTIFACTS / "raw-datasets").mkdir(exist_ok=True)
(ARTIFACTS / "normalized-datasets").mkdir(exist_ok=True)


def save_raw(provider: str, scenario: str, run: int, result) -> None:
    path = ARTIFACTS / "raw-datasets" / f"{provider}_{scenario}_run{run}.json"
    data = {
        "provider": result.provider,
        "scenario": result.scenario,
        "collected_at": result.collected_at,
        "duration_seconds": result.duration_seconds,
        "error": result.error,
        "records": len(result.contents),
        "contents": [
            {"id": c.id, "external_id": c.external_id, "url": c.url,
             "author": c.author, "published_at": c.published_at,
             "text": c.text[:200], "media_type": c.media_type,
             "hashtags": c.hashtags, "raw_metrics": c.raw_metrics}
            for c in result.contents[:20]
        ],
    }
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def save_normalized(provider: str, scenario: str, run: int, contents: list) -> None:
    path = ARTIFACTS / "normalized-datasets" / f"{provider}_{scenario}_run{run}.json"
    data = [
        {"id": c.id, "external_id": c.external_id, "url": c.url,
         "author": c.author, "published_at": c.published_at,
         "text": c.text[:200], "media_type": c.media_type,
         "hashtags": c.hashtags, "raw_metrics": c.raw_metrics}
        for c in contents
    ]
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


async def main() -> None:
    providers = [MetaOfficialProvider(), BrightDataProvider(), ApifyProvider()]
    results = {}

    for provider in providers:
        print(f"Testing {provider.name}...")
        provider_metrics = []

        for scenario in SCENARIOS:
            for run_idx in range(scenario.repeat_count):
                result = await provider.discover(scenario.query)
                result = type(result)(
                    provider=result.provider,
                    scenario=scenario.id,
                    query=result.query,
                    contents=result.contents,
                    raw_response=result.raw_response,
                    collected_at=result.collected_at,
                    duration_seconds=result.duration_seconds,
                    error=result.error,
                    cost_usd=result.cost_usd,
                )

                save_raw(provider.name, scenario.id, run_idx, result)
                normalized = normalize(result.contents)
                save_normalized(provider.name, scenario.id, run_idx, normalized)

                m = compute_metrics(result, 48)
                provider_metrics.append(m)

                print(f"  {scenario.id} run {run_idx}: {m.records_returned} records, error={m.error}")

        agg = aggregate_metrics(provider_metrics)
        dq = compute_discovery_quality(agg)
        tr = compute_trend_readiness(agg)
        er = compute_evidence_readiness(agg)

        results[provider.name] = {
            "aggregate": {
                "records_returned": agg.records_returned,
                "unique_records": agg.unique_records,
                "duplicate_rate": round(agg.duplicate_rate, 4),
                "freshness_rate": round(agg.freshness_rate, 4),
                "metadata_completeness": round(agg.metadata_completeness, 4),
                "creator_diversity": round(agg.creator_diversity, 4),
                "successful_runs": agg.successful_runs,
                "total_runs": agg.total_runs,
                "latency_seconds": round(agg.latency_seconds, 2),
                "cost_usd": agg.cost_usd,
                "error": agg.error,
            },
            "discovery_quality": {
                "freshness": dq.freshness, "coverage": dq.coverage,
                "metadata": dq.metadata, "reliability": dq.reliability,
                "diversity": dq.diversity, "cost": dq.cost,
                "validation": dq.validation, "total": dq.total,
            },
            "trend_readiness": {
                "temporal_data": tr.temporal_data, "creator_diversity": tr.creator_diversity,
                "engagement_metrics": tr.engagement_metrics,
                "deduplication_quality": tr.deduplication_quality, "total": tr.total,
            },
            "evidence_readiness": {
                "source_reliability": er.source_reliability,
                "metadata_depth": er.metadata_depth,
                "freshness": er.freshness, "repeatability": er.repeatability,
                "total": er.total,
            },
        }

        (ARTIFACTS / f"{provider.name}_results.json").write_text(
            json.dumps(results[provider.name], indent=2), encoding="utf-8"
        )

    generate_report(results, ARTIFACTS)

    for name, r in results.items():
        dq = r.get("discovery_quality", {}).get("total", 0)
        print(f"{name}: DQ={dq}")

    print("Benchmark complete.")


if __name__ == "__main__":
    asyncio.run(main())
