from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from benchmark.trend_detection.content_intelligence import ContentFeatures
from benchmark.trend_detection.clustering import ClusterData
from benchmark.trend_detection.temporal import TemporalSignal


@dataclass
class PatternSignal:
    pattern_type: str
    pattern_value: str
    count: int
    creator_count: int
    confidence: float


@dataclass
class PatternAnalysis:
    hashtag_patterns: list[PatternSignal]
    format_patterns: list[PatternSignal]
    structure_patterns: list[PatternSignal]
    engagement_patterns: list[PatternSignal]
    language_patterns: list[PatternSignal]
    niche_signals: list[str]


def detect_patterns(
    contents: list[ContentFeatures],
    temporal: TemporalSignal,
) -> PatternAnalysis:
    hashtag_patterns = _detect_hashtag_patterns(contents)
    format_patterns = _detect_format_patterns(contents)
    structure_patterns = _detect_structure_patterns(contents)
    engagement_patterns = _detect_engagement_patterns(contents)
    language_patterns = _detect_language_patterns(contents)
    niche_signals = _detect_niche_signals(contents)

    return PatternAnalysis(
        hashtag_patterns=hashtag_patterns,
        format_patterns=format_patterns,
        structure_patterns=structure_patterns,
        engagement_patterns=engagement_patterns,
        language_patterns=language_patterns,
        niche_signals=niche_signals,
    )


def _detect_hashtag_patterns(contents: list[ContentFeatures]) -> list[PatternSignal]:
    tag_authors: dict[str, set[str]] = {}
    for c in contents:
        for tag in c.hashtag_set:
            tag_authors.setdefault(tag, set()).add(c.author)

    patterns = []
    for tag, authors in tag_authors.items():
        if len(authors) >= 2:
            patterns.append(PatternSignal(
                pattern_type="hashtag",
                pattern_value=tag,
                count=len(authors),
                creator_count=len(authors),
                confidence=min(1.0, len(authors) / 5.0),
            ))

    patterns.sort(key=lambda p: p.count, reverse=True)
    return patterns[:20]


def _detect_format_patterns(contents: list[ContentFeatures]) -> list[PatternSignal]:
    format_authors: dict[str, set[str]] = {}
    for c in contents:
        format_authors.setdefault(c.media_type, set()).add(c.author)

    patterns = []
    for fmt, authors in format_authors.items():
        if len(authors) >= 2:
            patterns.append(PatternSignal(
                pattern_type="format",
                pattern_value=fmt,
                count=len(authors),
                creator_count=len(authors),
                confidence=min(1.0, len(authors) / 5.0),
            ))

    patterns.sort(key=lambda p: p.count, reverse=True)
    return patterns


def _detect_structure_patterns(contents: list[ContentFeatures]) -> list[PatternSignal]:
    structure_counts: dict[str, set[str]] = {}
    for c in contents:
        structure = _classify_structure(c)
        structure_counts.setdefault(structure, set()).add(c.author)

    patterns = []
    for struct, authors in structure_counts.items():
        if len(authors) >= 2:
            patterns.append(PatternSignal(
                pattern_type="structure",
                pattern_value=struct,
                count=len(authors),
                creator_count=len(authors),
                confidence=min(1.0, len(authors) / 5.0),
            ))

    patterns.sort(key=lambda p: p.count, reverse=True)
    return patterns


def _detect_engagement_patterns(contents: list[ContentFeatures]) -> list[PatternSignal]:
    patterns = []

    questions = [c for c in contents if c.has_question]
    if len(questions) >= 2:
        patterns.append(PatternSignal(
            pattern_type="engagement",
            pattern_value="has_question",
            count=len(questions),
            creator_count=len(set(c.author for c in questions)),
            confidence=min(1.0, len(questions) / 5.0),
        ))

    numbers = [c for c in contents if c.has_number]
    if len(numbers) >= 2:
        patterns.append(PatternSignal(
            pattern_type="engagement",
            pattern_value="has_number",
            count=len(numbers),
            creator_count=len(set(c.author for c in numbers)),
            confidence=min(1.0, len(numbers) / 5.0),
        ))

    ctas = [c for c in contents if c.has_cta]
    if len(ctas) >= 2:
        patterns.append(PatternSignal(
            pattern_type="engagement",
            pattern_value="has_cta",
            count=len(ctas),
            creator_count=len(set(c.author for c in ctas)),
            confidence=min(1.0, len(ctas) / 5.0),
        ))

    return patterns


def _detect_language_patterns(contents: list[ContentFeatures]) -> list[PatternSignal]:
    lang_authors: dict[str, set[str]] = {}
    for c in contents:
        for lang in c.language_hints:
            lang_authors.setdefault(lang, set()).add(c.author)

    patterns = []
    for lang, authors in lang_authors.items():
        patterns.append(PatternSignal(
            pattern_type="language",
            pattern_value=lang,
            count=len(authors),
            creator_count=len(authors),
            confidence=min(1.0, len(authors) / 5.0),
        ))

    return patterns


def _detect_niche_signals(contents: list[ContentFeatures]) -> list[str]:
    niche_tags = {
        "fitness": ["fitness", "gym", "workout", "bodybuilding", "treino", "musculacao", "personal"],
        "marketing": ["marketing", "digitalmarketing", "socialmediamarketing", "contentmarketing"],
        "beauty": ["beauty", "skincare", "makeup", "maquiagem", "beleza", "autocuidado"],
        "lifestyle": ["lifestyle", "thatgirl", "dailyroutine", "motivacao"],
        "business": ["business", "empreendedorismo", "entrepreneur", "finance"],
    }

    niche_counts: dict[str, int] = {}
    for c in contents:
        for niche, keywords in niche_tags.items():
            if c.hashtag_set & set(keywords):
                niche_counts[niche] = niche_counts.get(niche, 0) + 1

    return [n for n, _ in sorted(niche_counts.items(), key=lambda x: x[1], reverse=True) if niche_counts[n] >= 2]


def _classify_structure(c: ContentFeatures) -> str:
    parts = []
    if c.has_question:
        parts.append("question")
    if c.has_number:
        parts.append("number")
    if c.has_cta:
        parts.append("cta")
    if c.word_count > 50:
        parts.append("long")
    elif c.word_count < 10:
        parts.append("short")
    else:
        parts.append("medium")
    return "_".join(parts) if parts else "generic"
