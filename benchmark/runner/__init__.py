from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from benchmark.providers import DiscoveryProvider, DiscoveryQuery, DiscoveryResult
from benchmark.runner.scenarios import Scenario, SCENARIOS
from benchmark.metrics import (
    BenchmarkMetrics,
    DiscoveryQualityScore,
    TrendReadinessScore,
    EvidenceReadinessScore,
    compute_metrics,
    aggregate_metrics,
    compute_discovery_quality,
    compute_trend_readiness,
    compute_evidence_readiness,
)
from benchmark.normalization import normalize


class BenchmarkRunner:
    def __init__(self, providers: list[DiscoveryProvider], output_dir: Path) -> None:
        self.providers = providers
        self.output_dir = output_dir
        self.raw_dir = output_dir / "raw-datasets"
        self.normalized_dir = output_dir / "normalized-datasets"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.normalized_dir.mkdir(parents=True, exist_ok=True)

    async def run_all(self) -> dict:
        results: dict[str, dict] = {}

        for provider in self.providers:
            provider_results = await self._run_provider(provider)
            results[provider.name] = provider_results

        return results

    async def _run_provider(self, provider: DiscoveryProvider) -> dict:
        all_metrics: list[BenchmarkMetrics] = []
        all_results: list[DiscoveryResult] = []

        for scenario in SCENARIOS:
            scenario_results = await self._run_scenario(provider, scenario)
            all_results.extend(scenario_results)

            for result in scenario_results:
                metrics = compute_metrics(result, scenario_window_hours=48)
                all_metrics.append(metrics)

        agg = aggregate_metrics(all_metrics)
        dq = compute_discovery_quality(agg)
        tr = compute_trend_readiness(agg)
        er = compute_evidence_readiness(agg)

        self._save_provider_results(provider.name, all_results, all_metrics, agg, dq, tr, er)

        return {
            "metrics": [self._metrics_to_dict(m) for m in all_metrics],
            "aggregate": self._metrics_to_dict(agg),
            "discovery_quality": self._dq_to_dict(dq),
            "trend_readiness": self._tr_to_dict(tr),
            "evidence_readiness": self._er_to_dict(er),
        }

    async def _run_scenario(self, provider: DiscoveryProvider, scenario: Scenario) -> list[DiscoveryResult]:
        results: list[DiscoveryResult] = []

        for run_idx in range(scenario.repeat_count):
            try:
                result = await provider.discover(scenario.query)
                result = DiscoveryResult(
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
                results.append(result)

                self._save_raw(provider.name, scenario.id, run_idx, result)

                normalized = normalize(result.contents)
                self._save_normalized(provider.name, scenario.id, run_idx, normalized)

                if scenario.repeat_count > 1 and run_idx < scenario.repeat_count - 1:
                    await asyncio.sleep(scenario.repeat_interval_seconds)

            except Exception as e:
                results.append(DiscoveryResult(
                    provider=provider.name,
                    scenario=scenario.id,
                    query=scenario.query,
                    contents=[],
                    raw_response={"error": str(e)},
                    collected_at=datetime.now(timezone.utc).isoformat(),
                    duration_seconds=0,
                    error=str(e),
                ))

        return results

    def _save_raw(self, provider: str, scenario: str, run: int, result: DiscoveryResult) -> None:
        path = self.raw_dir / f"{provider}_{scenario}_run{run}.json"
        data = {
            "provider": result.provider,
            "scenario": result.scenario,
            "collected_at": result.collected_at,
            "duration_seconds": result.duration_seconds,
            "error": result.error,
            "cost_usd": result.cost_usd,
            "records": len(result.contents),
            "raw_response_sample": result.raw_response,
            "contents": [
                {
                    "id": c.id, "source": c.source, "external_id": c.external_id,
                    "url": c.url, "author": c.author, "published_at": c.published_at,
                    "text": c.text[:200], "media_type": c.media_type,
                    "hashtags": c.hashtags, "raw_metrics": c.raw_metrics,
                }
                for c in result.contents[:20]
            ],
        }
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def _save_normalized(self, provider: str, scenario: str, run: int, contents: list) -> None:
        path = self.normalized_dir / f"{provider}_{scenario}_run{run}.json"
        data = [
            {
                "id": c.id, "source": c.source, "external_id": c.external_id,
                "url": c.url, "author": c.author, "published_at": c.published_at,
                "collected_at": c.collected_at, "text": c.text[:200],
                "media_type": c.media_type, "hashtags": c.hashtags,
                "raw_metrics": c.raw_metrics,
            }
            for c in contents
        ]
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def _save_provider_results(self, provider: str, results, metrics, agg, dq, tr, er) -> None:
        path = self.output_dir / f"{provider}_results.json"
        data = {
            "provider": provider,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_runs": len(results),
            "aggregate": self._metrics_to_dict(agg),
            "discovery_quality": self._dq_to_dict(dq),
            "trend_readiness": self._tr_to_dict(tr),
            "evidence_readiness": self._er_to_dict(er),
        }
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def _metrics_to_dict(self, m: BenchmarkMetrics) -> dict:
        return {
            "provider": m.provider, "scenario": m.scenario,
            "records_returned": m.records_returned, "unique_records": m.unique_records,
            "duplicate_rate": round(m.duplicate_rate, 4),
            "freshness_rate": round(m.freshness_rate, 4),
            "metadata_completeness": round(m.metadata_completeness, 4),
            "creator_diversity": round(m.creator_diversity, 4),
            "successful_runs": m.successful_runs, "total_runs": m.total_runs,
            "latency_seconds": round(m.latency_seconds, 2),
            "cost_usd": m.cost_usd, "error": m.error,
        }

    def _dq_to_dict(self, dq: DiscoveryQualityScore) -> dict:
        return {
            "freshness": dq.freshness, "coverage": dq.coverage,
            "metadata": dq.metadata, "reliability": dq.reliability,
            "diversity": dq.diversity, "cost": dq.cost,
            "validation": dq.validation, "total": dq.total,
        }

    def _tr_to_dict(self, tr: TrendReadinessScore) -> dict:
        return {
            "temporal_data": tr.temporal_data, "creator_diversity": tr.creator_diversity,
            "engagement_metrics": tr.engagement_metrics,
            "deduplication_quality": tr.deduplication_quality, "total": tr.total,
        }

    def _er_to_dict(self, er: EvidenceReadinessScore) -> dict:
        return {
            "source_reliability": er.source_reliability,
            "metadata_depth": er.metadata_depth,
            "freshness": er.freshness, "repeatability": er.repeatability,
            "total": er.total,
        }
