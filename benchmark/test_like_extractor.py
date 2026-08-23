#!/usr/bin/env python
"""Unit tests for like scale normalization and evidence persistence."""

import sys
sys.path.insert(0, "C:/Users/rafael.dacosta/source/repos/AI Trend Scout")

from benchmark.browser_discovery.extraction_v3 import extract_like_count, extract_comment_count


def test_integer_likes():
    """Test integer likes without suffix."""
    value, raw, source = extract_like_count("123 likes")
    assert value == 123, f"Expected 123, got {value}"
    assert raw == "123 likes", f"Expected '123 likes', got {raw}"
    assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_integer_likes")


def test_k_likes():
    """Test K suffix scaling."""
    value, raw, source = extract_like_count("1K likes")
    assert value == 1000, f"Expected 1000, got {value}"
    assert raw == "1K likes", f"Expected '1K likes', got {raw}"
    assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_k_likes")


def test_16k_likes():
    """Test 16K likes scaling."""
    value, raw, source = extract_like_count("16K likes")
    assert value == 16000, f"Expected 16000, got {value}"
    assert raw == "16K likes", f"Expected '16K likes', got {raw}"
    assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_16k_likes")


def test_271k_likes():
    """Test 271K likes scaling - forensic case."""
    value, raw, source = extract_like_count("271K likes")
    assert value == 271000, f"Expected 271000, got {value}"
    assert raw == "271K likes", f"Expected '271K likes', got {raw}"
    assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_271k_likes")


def test_1_5k_likes():
    """Test decimal K scaling."""
    value, raw, source = extract_like_count("1.5K likes")
    assert value == 1500, f"Expected 1500, got {value}"
    assert raw == "1.5K likes", f"Expected '1.5K likes', got {raw}"
    assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_1_5k_likes")


def test_m_likes():
    """Test M suffix scaling."""
    value, raw, source = extract_like_count("1M likes")
    assert value == 1000000, f"Expected 1000000, got {value}"
    assert raw == "1M likes", f"Expected '1M likes', got {raw}"
    assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_m_likes")


def test_1_5m_likes():
    """Test decimal M scaling."""
    value, raw, source = extract_like_count("1.5M likes")
    assert value == 1500000, f"Expected 1500000, got {value}"
    assert raw == "1.5M likes", f"Expected '1.5M likes', got {raw}"
    assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_1_5m_likes")


def test_b_likes():
    """Test B suffix scaling."""
    value, raw, source = extract_like_count("1B likes")
    assert value == 1000000000, f"Expected 1000000000, got {value}"
    assert raw == "1B likes", f"Expected '1B likes', got {raw}"
    assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_b_likes")


def test_evidence_persistence_integer():
    """Test evidence persistence for integer likes."""
    value, raw, source = extract_like_count("123 likes")
    assert value == 123
    assert raw == "123 likes"
    assert source == "TEXT_OG"
    print("OK test_evidence_persistence_integer")


def test_evidence_persistence_k():
    """Test evidence persistence for K scaled likes."""
    value, raw, source = extract_like_count("271K likes")
    assert value == 271000
    assert raw == "271K likes"
    assert source == "TEXT_OG"
    print("OK test_evidence_persistence_k")


def test_no_like():
    """Test absence of like returns null."""
    value, raw, source = extract_like_count("no likes here")
    assert value is None, f"Expected None, got {value}"
    assert raw is None, f"Expected None, got {raw}"
    assert source is None, f"Expected None, got {source}"
    print("OK test_no_like")


def test_forensic_cases():
    """Test the 6 forensic cases from V3.2/V3.3 audit."""
    cases = [
        ("271K likes", 271000),
        ("621K likes", 621000),
        ("198K likes", 198000),
        ("67K likes", 67000),
        ("47K likes", 47000),
        ("16K likes", 16000),
    ]
    for text, expected in cases:
        value, raw, source = extract_like_count(text)
        assert value == expected, f"For {text}: expected {expected}, got {value}"
        assert source == "TEXT_OG", f"Expected TEXT_OG, got {source}"
    print("OK test_forensic_cases")


def test_comma_and_dot_handling():
    """Test comma and dot handling in numbers."""
    value, _, _ = extract_like_count("1,234 likes")
    assert value == 1234, f"Expected 1234, got {value}"
    
    value, _, _ = extract_like_count("1.5K likes")
    assert value == 1500, f"Expected 1500, got {value}"
    
    value, _, _ = extract_like_count("12,345 likes")
    assert value == 12345, f"Expected 12345, got {value}"
    
    value, _, _ = extract_like_count("1.5K likes")
    assert value == 1500
    print("OK test_comma_and_dot_handling")


def test_comment_count_scale():
    """Test comment count scale normalization."""
    value, raw, source = extract_comment_count("621K comments")
    assert value == 621000
    assert raw == "621K comments"
    assert source == "TEXT_OG"
    
    value, _, _ = extract_comment_count("4,378 comments")
    assert value == 4378
    
    value, _, _ = extract_comment_count("1.5M comments")
    assert value == 1500000
    print("OK test_comment_count_scale")


def test_integer_preserved():
    """Ensure integer values without suffix are preserved correctly."""
    value, _, _ = extract_like_count("999 likes")
    assert value == 999
    
    value, _, _ = extract_like_count("0 likes")
    assert value == 0
    
    value, _, _ = extract_like_count("999999 likes")
    assert value == 999999
    print("OK test_integer_preserved")


if __name__ == "__main__":
    print("Running like extractor unit tests...\n")
    
    test_integer_likes()
    test_k_likes()
    test_16k_likes()
    test_271k_likes()
    test_1_5k_likes()
    test_m_likes()
    test_1_5m_likes()
    test_b_likes()
    test_evidence_persistence_integer()
    test_evidence_persistence_k()
    test_no_like()
    test_forensic_cases()
    test_comma_and_dot_handling()
    test_comment_count_scale()
    test_integer_preserved()
    
    print("\nOK All tests passed!")