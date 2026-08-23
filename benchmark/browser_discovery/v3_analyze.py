import json
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")

data = json.loads(open("artifacts/browser-discovery/v2/browser-discovery-v2.json").read())
posts = data.get("enriched_posts", [])

print("=== Text patterns (first 80 chars each) ===")
for p in posts[:8]:
    text = str(p.get("text", ""))[:100]
    print(f"--- {p.get('content_id')}")
    print(f"  {text}")

print()
print("=== Author patterns ===")
for p in posts[:8]:
    text = str(p.get("text", ""))
    # Pattern 1: "465 likes, 53 comments - username on ..."
    # Pattern 2: "username on ...: "
    import re
    m1 = re.search(r"-\s*([a-zA-Z0-9_.]+)\s+on\s+", text)
    m2 = re.search(r"^([a-zA-Z0-9_.]+)\s+on\s+", text)
    author = None
    if m1:
        author = m1.group(1)
    elif m2:
        author = m2.group(1)
    print(f"  {p.get('content_id')}: author={author} (m1={bool(m1)}, m2={bool(m2)})")

print()
print("=== Comment patterns ===")
for p in posts[:8]:
    text = str(p.get("text", ""))
    import re
    m = re.search(r"([\d,\.K]+)\s+comments?", text, re.IGNORECASE)
    comments = None
    if m:
        raw = m.group(1)
        if "K" in raw:
            comments = int(float(raw.replace("K", "")) * 1000)
        else:
            comments = int(raw.replace(",", "").replace(".", ""))
    print(f"  {p.get('content_id')}: comments={comments}")