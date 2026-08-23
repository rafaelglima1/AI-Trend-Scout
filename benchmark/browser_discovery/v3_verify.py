import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from benchmark.browser_discovery.extraction_v3 import extract_author, extract_comment_count, classify_media_type

data = json.loads(open("artifacts/browser-discovery/v2/browser-discovery-v2.json").read())
posts = data.get("enriched_posts", [])

print("=== V3 Extraction on V2 Data ===")
author_ok = 0
comment_ok = 0
media_ok = 0

for p in posts:
    text = str(p.get("text", ""))
    url = p.get("url", "")

    author = extract_author(text)
    comments = extract_comment_count(text)

    media_type, is_video, is_reel = classify_media_type(text + " " + p.get("hashtags", []).__str__(), text, url)

    if author:
        author_ok += 1
    if comments is not None:
        comment_ok += 1
    if media_type != "UNKNOWN":
        media_ok += 1

    print(f"  {p.get('content_id')}: author={author}, comments={comments}, media={media_type}")

print()
print(f"Author: {author_ok}/{len(posts)} ({author_ok/len(posts):.0%})")
print(f"Comments: {comment_ok}/{len(posts)} ({comment_ok/len(posts):.0%})")
print(f"Media type: {media_ok}/{len(posts)} ({media_ok/len(posts):.0%})")
