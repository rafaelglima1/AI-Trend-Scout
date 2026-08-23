import json

data = json.loads(open("artifacts/browser-discovery/v2/browser-discovery-v2.json").read())
posts = data.get("enriched_posts", [])
print(f"Total: {len(posts)}")
print()
for p in posts[:3]:
    cid = p.get("content_id", "")
    author = p.get("author", "")
    text = str(p.get("text", ""))[:60]
    likes = p.get("like_count")
    comments = p.get("comment_count")
    views = p.get("view_count")
    published = p.get("published_at")
    media = p.get("media_type")
    print(f"ID: {cid}")
    print(f"Author: {author}")
    print(f"Text: {text}")
    print(f"Likes: {likes}")
    print(f"Comments: {comments}")
    print(f"Views: {views}")
    print(f"Published: {published}")
    print(f"Media: {media}")
    print()
