from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime, timezone

from benchmark.browser_discovery.config import BrowserConfig, SCENARIOS
from benchmark.browser_discovery.browser import BrowserManager
from benchmark.browser_discovery.extractor import extract_contents
from benchmark.browser_discovery.normalizer import normalize_contents
from benchmark.browser_discovery.metrics import compute_metrics, BrowserMetrics
from benchmark.browser_discovery.report import generate_report


ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS = ROOT / "artifacts" / "browser-discovery"
RAW_DIR = ARTIFACTS / "raw"
NORM_DIR = ARTIFACTS / "normalized"
SCREENSHOTS_DIR = ARTIFACTS / "screenshots"


async def run_poc(headless: bool = True, max_per_scenario: int = 30) -> None:
    config = BrowserConfig(
        headless=headless,
        max_per_scenario=min(max_per_scenario, 30),
    )

    print("Browser Discovery POC")
    print("=" * 50)
    print(f"Headless: {config.headless}")
    print(f"Max per scenario: {config.max_per_scenario}")
    print(f"Max total: {config.max_total_contents}")
    print("=" * 50)

    manager = BrowserManager(config)
    page = await manager.start()

    all_raw: dict[str, list[dict]] = {}
    all_normalized: dict[str, list[dict]] = {}
    scenario_results: list[dict] = []
    total_contents = 0
    blocked = False
    auth_required = False
    captcha_detected = False
    start_time = time.monotonic()

    try:
        for scenario in SCENARIOS:
            if total_contents >= config.max_total_contents:
                print(f"\nReached total limit ({config.max_total_contents}). Stopping.")
                break

            print(f"\n--- Scenario: {scenario['id']} ---")
            remaining = config.max_total_contents - total_contents
            scenario_limit = min(config.max_per_scenario, remaining)

            result = await _run_scenario(page, manager, scenario, scenario_limit, config)
            scenario_results.append(result)

            raw_contents = result.get("raw_contents", [])
            all_raw[scenario["id"]] = raw_contents

            normalized = normalize_contents(raw_contents, scenario["id"])
            all_normalized[scenario["id"]] = normalized

            total_contents += len(normalized)
            print(f"  Records: {len(normalized)} (total: {total_contents})")

            if result.get("auth_required"):
                auth_required = True
                print("  AUTH_REQUIRED detected. Stopping.")
                break
            if result.get("blocked"):
                blocked = True
                print("  BLOCKED detected. Stopping.")
                break
            if result.get("captcha"):
                captcha_detected = True
                print("  CAPTCHA detected. Stopping.")
                break

    finally:
        await manager.stop()

    duration = time.monotonic() - start_time

    successful = sum(1 for sr in scenario_results if sr.get("status") == "SUCCESS")

    all_normalized_flat = []
    for contents in all_normalized.values():
        all_normalized_flat.extend(contents)

    metrics = compute_metrics(
        contents=all_normalized_flat,
        total_scenarios=len(SCENARIOS),
        successful_scenarios=successful,
        duration=duration,
        blocked=blocked,
        auth_required=auth_required,
        captcha=captcha_detected,
    )

    _save_raw(all_raw)
    _save_normalized(all_normalized)

    generate_report(metrics, scenario_results, all_raw, all_normalized, ARTIFACTS)

    print("\n" + "=" * 50)
    print(f"Records: {metrics.records_returned}")
    print(f"Unique: {metrics.unique_records}")
    print(f"Creators: {metrics.unique_creators}")
    print(f"Auth Required: {metrics.auth_required}")
    print(f"Blocked: {metrics.blocked}")
    print(f"Duration: {metrics.browser_duration_seconds:.2f}s")
    print("=" * 50)


async def _run_scenario(
    page, manager: BrowserManager, scenario: dict, limit: int, config: BrowserConfig
) -> dict:
    result = {
        "id": scenario["id"],
        "url": scenario["url"],
        "status": "PENDING",
        "records": 0,
        "error": None,
        "auth_required": False,
        "blocked": False,
        "captcha": False,
        "raw_contents": [],
    }

    try:
        success, error = await manager.navigate(scenario["url"])
        if not success:
            result["status"] = "NAVIGATION_FAILED"
            result["error"] = error
            return result

        if await manager.check_auth_required():
            result["status"] = "AUTH_REQUIRED"
            result["auth_required"] = True
            result["error"] = "AUTH_REQUIRED"
            return result

        if await manager.check_captcha():
            result["status"] = "CAPTCHA"
            result["captcha"] = True
            result["error"] = "CAPTCHA"
            return result

        await asyncio.sleep(2)

        contents = await extract_contents(page, limit)
        result["raw_contents"] = contents
        result["records"] = len(contents)
        result["status"] = "SUCCESS" if contents else "NO_CONTENT"

        if not contents:
            screenshot_path = SCREENSHOTS_DIR / f"{scenario['id']}_no_content.png"
            await manager.save_screenshot(screenshot_path)

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)[:200]
        screenshot_path = SCREENSHOTS_DIR / f"{scenario['id']}_error.png"
        await manager.save_screenshot(screenshot_path)

    return result


def _save_raw(raw_contents: dict[str, list[dict]]) -> None:
    for scenario_id, contents in raw_contents.items():
        path = RAW_DIR / f"scenario_{scenario_id}.json"
        path.write_text(json.dumps(contents, indent=2, default=str), encoding="utf-8")


def _save_normalized(normalized: dict[str, list[dict]]) -> None:
    for scenario_id, contents in normalized.items():
        path = NORM_DIR / f"scenario_{scenario_id}.json"
        path.write_text(json.dumps(contents, indent=2, default=str), encoding="utf-8")
