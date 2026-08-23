from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from benchmark.trend_detection.content_intelligence import ContentFeatures


@dataclass
class ClusterResult:
    clusters: list[ClusterData]
    noise: list[ContentFeatures]


@dataclass
class ClusterData:
    id: str
    contents: list[ContentFeatures]
    primary_hashtags: list[str]
    dominant_format: str
    hashtag_signature: str
    text_signature: str


def cluster_by_hashtag_similarity(
    contents: list[ContentFeatures],
    min_overlap: int = 2,
) -> ClusterResult:
    hashtag_index: dict[frozenset, list[ContentFeatures]] = {}

    for c in contents:
        if not c.hashtag_set:
            continue
        sig = frozenset(c.hashtag_set)
        hashtag_index.setdefault(sig, []).append(c)

    merged = _merge_overlapping_clusters(hashtag_index, min_overlap)

    clustered_ids: set[str] = set()
    clusters: list[ClusterData] = []

    for idx, (sig, group) in enumerate(merged.items()):
        if len(group) < 2:
            continue
        clustered_ids.update(c.content_id for c in group)
        tag_counts = Counter()
        for c in group:
            tag_counts.update(c.hashtag_set)
        primary = [t for t, _ in tag_counts.most_common(5)]

        format_counts = Counter(c.media_type for c in group)
        dominant = format_counts.most_common(1)[0][0] if format_counts else "unknown"

        clusters.append(ClusterData(
            id=f"cluster_{idx:04d}",
            contents=group,
            primary_hashtags=primary,
            dominant_format=dominant,
            hashtag_signature=",".join(sorted(sig)),
            text_signature=_text_signature(group),
        ))

    noise = [c for c in contents if c.content_id not in clustered_ids]

    clusters.sort(key=lambda c: len(c.contents), reverse=True)

    return ClusterResult(clusters=clusters, noise=noise)


def cluster_by_text_similarity(
    contents: list[ContentFeatures],
    min_overlap: float = 0.3,
) -> ClusterResult:
    n = len(contents)
    if n == 0:
        return ClusterResult(clusters=[], noise=[])

    token_sets = [set(c.text_tokens) for c in contents]
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i in range(n):
        for j in range(i + 1, n):
            if not token_sets[i] or not token_sets[j]:
                continue
            intersection = token_sets[i] & token_sets[j]
            union_size = len(token_sets[i] | token_sets[j])
            if union_size > 0 and len(intersection) / union_size >= min_overlap:
                union(i, j)

    groups: dict[int, list[ContentFeatures]] = {}
    for i in range(n):
        root = find(i)
        groups.setdefault(root, []).append(contents[i])

    clustered_ids: set[str] = set()
    clusters: list[ClusterData] = []

    for idx, (root, group) in enumerate(groups.items()):
        if len(group) < 2:
            continue
        clustered_ids.update(c.content_id for c in group)

        tag_counts = Counter()
        for c in group:
            tag_counts.update(c.hashtag_set)
        primary = [t for t, _ in tag_counts.most_common(5)]

        format_counts = Counter(c.media_type for c in group)
        dominant = format_counts.most_common(1)[0][0] if format_counts else "unknown"

        all_tokens = set()
        for c in group:
            all_tokens.update(c.text_tokens)
        text_sig = ",".join(sorted(all_tokens)[:10])

        clusters.append(ClusterData(
            id=f"txtcluster_{idx:04d}",
            contents=group,
            primary_hashtags=primary,
            dominant_format=dominant,
            hashtag_signature=",".join(sorted(tag_counts.keys())[:10]),
            text_signature=text_sig,
        ))

    noise = [c for c in contents if c.content_id not in clustered_ids]
    clusters.sort(key=lambda c: len(c.contents), reverse=True)

    return ClusterResult(clusters=clusters, noise=noise)


def _merge_overlapping_clusters(
    index: dict[frozenset, list[ContentFeatures]],
    min_overlap: int,
) -> dict[frozenset, list[ContentFeatures]]:
    signatures = list(index.keys())
    merged: dict[int, list[ContentFeatures]] = {}
    assignment = list(range(len(signatures)))

    def find(x: int) -> int:
        while assignment[x] != x:
            assignment[x] = assignment[assignment[x]]
            x = assignment[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px != py:
            assignment[px] = py

    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            overlap = len(signatures[i] & signatures[j])
            if overlap >= min_overlap:
                union(i, j)

    groups: dict[int, list[ContentFeatures]] = {}
    for i in range(len(signatures)):
        root = find(i)
        groups.setdefault(root, []).extend(index[signatures[i]])

    return {frozenset(): contents for _, contents in groups.items()}


def _text_signature(group: list[ContentFeatures]) -> str:
    word_counts = Counter()
    for c in group:
        word_counts.update(c.text_tokens)
    return ",".join(w for w, _ in word_counts.most_common(10))
