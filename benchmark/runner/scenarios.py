from __future__ import annotations

from dataclasses import dataclass, field

from benchmark.providers import DiscoveryMode, DiscoveryQuery


@dataclass
class Scenario:
    id: str
    name: str
    description: str
    query: DiscoveryQuery
    repeat_count: int = 3
    repeat_interval_seconds: int = 5
    expected_min_records: int = 10


SCENARIOS: list[Scenario] = [
    Scenario(
        id="SCENARIO-001",
        name="BR Reels Keywords",
        description="Brazil + Reels + 10 niche keywords",
        query=DiscoveryQuery(
            source="instagram",
            mode=DiscoveryMode.EXPLORATION,
            keywords=["marketing", "fitness", "beleza", "odontologia", "finanças",
                       "empreendedorismo", "moda", "gastronomia", "tecnologia", "lifestyle"],
            region="BR",
            content_type="reels",
            limit=100,
        ),
        repeat_count=3,
        expected_min_records=50,
    ),
    Scenario(
        id="SCENARIO-002",
        name="Generic Discovery",
        description="Broad discovery without specific keywords",
        query=DiscoveryQuery(
            source="instagram",
            mode=DiscoveryMode.EXPLORATION,
            keywords=["trending"],
            region="BR",
            limit=100,
        ),
        repeat_count=3,
        expected_min_records=20,
    ),
    Scenario(
        id="SCENARIO-003",
        name="Temporal Repetition",
        description="Same query repeated to measure temporal changes",
        query=DiscoveryQuery(
            source="instagram",
            mode=DiscoveryMode.EXPLORATION,
            keywords=["fitness"],
            region="BR",
            limit=50,
        ),
        repeat_count=3,
        repeat_interval_seconds=5,
        expected_min_records=10,
    ),
    Scenario(
        id="SCENARIO-004",
        name="Profile Monitoring",
        description="Monitor public profiles for format changes",
        query=DiscoveryQuery(
            source="instagram",
            mode=DiscoveryMode.MONITORING,
            keywords=[],
            profile_url="https://www.instagram.com/instagram/",
            limit=50,
        ),
        repeat_count=1,
        expected_min_records=5,
    ),
]


def get_scenario(scenario_id: str) -> Scenario | None:
    for s in SCENARIOS:
        if s.id == scenario_id:
            return s
    return None


def list_scenarios() -> list[Scenario]:
    return list(SCENARIOS)
