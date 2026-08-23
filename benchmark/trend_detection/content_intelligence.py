from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ContentFeatures:
    content_id: str
    author: str
    published_at: str | None
    text: str
    media_type: str
    hashtags: list[str]
    text_tokens: list[str]
    hashtag_set: set[str]
    has_engagement: bool
    like_count: int | None
    comment_count: int | None
    word_count: int
    has_question: bool
    has_number: bool
    has_cta: bool
    language_hints: list[str]


@dataclass
class Cluster:
    id: str
    pattern: str
    contents: list[ContentFeatures]
    primary_hashtags: list[str]
    dominant_format: str
    creator_count: int
    time_span_hours: float
    growth_signal: float
    replication_signal: float
    cross_niche_signal: float
    engagement_signal: float


def extract_features(content: dict) -> ContentFeatures:
    text = content.get("text", "")
    hashtags = content.get("hashtags", [])
    metrics = content.get("raw_metrics", {})

    tokens = _tokenize(text)
    hashtag_set = set(h.lower() for h in hashtags)

    like_count = metrics.get("like_count")
    comment_count = metrics.get("comments_count")
    has_engagement = (like_count is not None and like_count > 0) or (comment_count is not None and comment_count > 0)

    return ContentFeatures(
        content_id=content.get("id", ""),
        author=content.get("author", "unknown"),
        published_at=content.get("published_at"),
        text=text,
        media_type=content.get("media_type", "unknown"),
        hashtags=hashtags,
        text_tokens=tokens,
        hashtag_set=hashtag_set,
        has_engagement=has_engagement,
        like_count=like_count,
        comment_count=comment_count,
        word_count=len(tokens),
        has_question="?" in text,
        has_number=bool(re.search(r"\d+", text)),
        has_cta=_has_cta(text),
        language_hints=_detect_language(text),
    )


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    stop_words = {
        "o", "a", "e", "de", "do", "da", "em", "um", "uma", "para", "com",
        "is", "the", "a", "an", "in", "on", "at", "to", "for", "of", "and",
        "or", "but", "not", "with", "this", "that", "it", "from", "by", "as",
        "be", "are", "was", "were", "has", "have", "had", "can", "will",
        "the", "your", "you", "my", "me", "we", "they", "he", "she",
        "el", "la", "los", "las", "en", "un", "una", "por", "con",
        "le", "les", "des", "du", "et", "est", "qui", "que", "se",
    }
    return [t for t in tokens if t not in stop_words and len(t) > 1]


def _has_cta(text: str) -> bool:
    cta_patterns = [
        r"comenta", r"comment", r"share", r"compartilha",
        r"salva", r"save", r"link", r"clique", r"click",
        r"follow", r"segue", r"dm", r"link in bio",
    ]
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in cta_patterns)


def _detect_language(text: str) -> list[str]:
    hints = []
    pt_words = {"voce", "que", "nao", "mais", "com", "para", "como", "isso", "muito", "bom", "todo", "tudo", "fazer"}
    en_words = {"you", "that", "this", "with", "from", "have", "will", "make", "just", "like", "best", "top"}
    es_words = {"que", "como", "para", "pero", "mas", "todo", "hacer", "puede", "tiene", "bien"}

    tokens = set(text.lower().split())
    if tokens & pt_words:
        hints.append("pt")
    if tokens & en_words:
        hints.append("en")
    if tokens & es_words:
        hints.append("es")
    return hints
