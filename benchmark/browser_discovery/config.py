from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BrowserConfig:
    headless: bool = True
    max_per_scenario: int = 30
    max_total_contents: int = 90
    max_scrolls_per_scenario: int = 5
    max_browser_sessions: int = 1
    max_run_duration_seconds: int = 180
    timeout_ms: int = 30000
    viewport_width: int = 1280
    viewport_height: int = 720


SCENARIOS = [
    {"id": "fitness", "hashtag": "fitness", "url": "https://www.instagram.com/explore/tags/fitness/"},
    {"id": "beleza", "hashtag": "beleza", "url": "https://www.instagram.com/explore/tags/beleza/"},
    {"id": "marketing", "hashtag": "marketing", "url": "https://www.instagram.com/explore/tags/marketing/"},
]
