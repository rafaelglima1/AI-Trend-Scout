from __future__ import annotations

import re
from typing import Any


def extract_author(text: str) -> str | None:
    if not text:
        return None
    m = re.search(r"-\s*([a-zA-Z0-9_.]+)\s+on\s+", text)
    if m:
        author = m.group(1)
        if not author or author in ("instagram", "whatsapp", "meta"):
            return None
        return author
    m = re.search(r"^([a-zA-Z0-9_.]+)\s+on\s+", text)
    if m:
        author = m.group(1)
        if not author or author in ("instagram", "whatsapp", "meta"):
            return None
        return author
    return None


def extract_comment_count(text: str) -> tuple[int | None, str | None, str | None]:
    if not text:
        return None, None, None
    
    m = re.search(r"([\d,\.]+)\s*([KMBkmb]?)\s*comments?", text, re.IGNORECASE)
    if not m:
        return None, None, None
    
    raw_num = m.group(1)
    suffix = m.group(2).upper() if m.group(2) else ""
    raw_match = m.group(0)
    
    try:
        num = float(raw_num.replace(",", ""))
        
        if suffix == "K":
            value = int(num * 1000)
        elif suffix == "M":
            value = int(num * 1_000_000)
        elif suffix == "B":
            value = int(num * 1_000_000_000)
        else:
            value = int(num)
        
        return value, raw_match, "TEXT_OG"
    except ValueError:
        return None, None, None


def extract_like_count(text: str) -> tuple[int | None, str | None, str | None]:
    if not text:
        return None, None, None
    
    m = re.search(r"([\d,\.]+)\s*([KMBkmb]?)\s*likes?", text, re.IGNORECASE)
    if not m:
        return None, None, None
    
    raw_num = m.group(1)
    suffix = m.group(2).upper() if m.group(2) else ""
    raw_match = m.group(0)
    
    try:
        num = float(raw_num.replace(",", ""))
        
        if suffix == "K":
            value = int(num * 1000)
        elif suffix == "M":
            value = int(num * 1_000_000)
        elif suffix == "B":
            value = int(num * 1_000_000_000)
        else:
            value = int(num)
        
        return value, raw_match, "TEXT_OG"
    except ValueError:
        return None, None, None


def classify_media_type(html: str, text: str, url: str) -> tuple[str, bool, bool]:
    is_video = False
    is_reel = "/reel/" in url
    media_type = "UNKNOWN"

    if is_reel:
        is_video = True
        media_type = "REEL"
        return media_type, is_video, is_reel

    video_indicators = [
        'og:type="video', '"og:type":"video', 'property="og:video"',
        "VideoObject", '"@type":"VideoObject"', '"content_type":"video"',
    ]
    for indicator in video_indicators:
        if indicator.lower() in html.lower():
            is_video = True
            break

    carousel_indicators = [
        '"@type":"CarouselMedia"', 'carousel_media', '"@type":"ImageGallery"',
        "sidecar",
    ]
    is_carousel = any(ind.lower() in html.lower() for ind in carousel_indicators)

    if is_carousel:
        media_type = "CAROUSEL"
    elif is_video:
        media_type = "VIDEO"
    else:
        image_indicators = ['og:image', '"og:image"', '"content_type":"image"']
        if any(ind.lower() in html.lower() for ind in image_indicators):
            media_type = "IMAGE"

    return media_type, is_video, is_reel
