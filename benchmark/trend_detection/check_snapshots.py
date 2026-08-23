import json
from pathlib import Path

snapshots_dir = Path("artifacts/temporal-snapshots")
for f in sorted(snapshots_dir.glob("snapshot_*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    sid = data["snapshot_id"]
    count = data["content_count"]
    started = data["started_at"][:19]
    contents = data.get("contents", [])
    ids = set(c.get("external_id", "") for c in contents)
    authors = set(c.get("author", "") for c in contents)
    first_id = contents[0].get("external_id", "") if contents else ""
    first_author = contents[0].get("author", "") if contents else ""

    print(f"{sid}: {count} records, started at {started}")
    print(f"  Unique IDs: {len(ids)}")
    print(f"  Authors: {authors}")
    print(f"  First item: {first_id} by {first_author}")

# Compare T0 and T3
t0 = json.loads((snapshots_dir / "snapshot_T0.json").read_text(encoding="utf-8"))
t3 = json.loads((snapshots_dir / "snapshot_T3.json").read_text(encoding="utf-8"))

t0_ids = set(c.get("external_id", "") for c in t0.get("contents", []))
t3_ids = set(c.get("external_id", "") for c in t3.get("contents", []))

common = t0_ids & t3_ids
new_in_t3 = t3_ids - t0_ids
removed_from_t0 = t0_ids - t3_ids

print(f"\nComparison T0 vs T3:")
print(f"  Common: {len(common)}")
print(f"  New in T3: {len(new_in_t3)}")
print(f"  Removed from T0: {len(removed_from_t0)}")
