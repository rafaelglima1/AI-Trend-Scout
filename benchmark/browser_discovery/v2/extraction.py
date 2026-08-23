from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent.parent


def extract_author(text: str) -> str | None:
    if not text:
        return None
    
    patterns = [
        r"-\s*([a-zA-Z0-9_.]+)\s+on\s+",
        r"^([a-zA-Z0-9_.]+)\s+on\s+",
        r"^([a-zA-Z0-9_.]+)\s+-\s+",
        r"-\s*([a-zA-Z0-9_.]+)\s+-\s+",
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            author = m.group(1)
            if not author or len(author) < 2:
                continue
            if author.lower() in ("instagram", "whatsapp", "meta", "and"):
                continue
            return author
    
    return None


def extract_comment_count(text: str) -> tuple[int | None, str | None, str | None]:
    if not text:
        return None, None, None
    
    patterns = [
        r"([\d,\.]+)\s*([KMBkmb]?)\s*comments?",
        r"([\d,\.]+)\s*([KMBkmb]?)\s*comment",
        r"comments?\s*:?\s*([\d,\.]+)\s*([KMBkmb]?)",
        r"([\d,\.]+)\s*([KMBkmb]?)\s*coms?",
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
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
                continue
    
    return None, None, None


def extract_like_count(text: str) -> tuple[int | None, str | None, str | None]:
    if not text:
        return None, None, None
    
    patterns = [
        r"([\d,\.]+)\s*([KMBkmb]?)\s*likes?",
        r"([\d,\.]+)\s*([KMBkmb]?)\s*like",
        r"likes?\s*:?\s*([\d,\.]+)\s*([KMBkmb]?)",
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
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
                continue
    
    return None, None, None


def classify_media_type(html: str, text: str, url: str) -> tuple[str, bool, bool]:
    is_video = False
    is_reel = "/reel/" in url

    if is_reel:
        return "REEL", True, True

    html_lower = html.lower()

    video_indicators = [
        'og:type="video', '"og:type":"video', 'property="og:video"',
        'og:video:url', 'og:video:type', 'og:video:width', 'og:video:height',
        'twitter:player', 'twitter:player:width', 'twitter:player:height',
        '"@type":"VideoObject"', 'videoobject', '"content_type":"video"',
        '"media_type":"video"', '"type":"video"', 'video/mp4',
    ]
    for indicator in video_indicators:
        if indicator in html_lower:
            is_video = True
            break

    carousel_indicators = [
        '"@type":"CarouselMedia"', 'carouselmedia', 'carousel media',
        '"@type":"ImageGallery"', 'imagegallery', 'image gallery',
        'sidecar', 'multi_image', 'multiple_images', 'carousel',
    ]
    is_carousel = any(indicator in html_lower for indicator in carousel_indicators)

    if is_carousel:
        return "CAROUSEL", False, False

    if is_video:
        return "VIDEO", True, False

    image_indicators = [
        'og:image', 'og:image:url', 'og:image:type', 'og:image:width', 'og:image:height',
        'twitter:image', 'twitter:image:src', 'thumbnail_url',
        '"@type":"ImageObject"', 'imageobject', 'image_object',
        '"content_type":"image"', '"media_type":"image"', 'image/jpeg',
        '"type":"image"', 'image/',
    ]
    is_image = any(indicator in html_lower for indicator in image_indicators)

    if is_image:
        return "IMAGE", False, False

    return "UNKNOWN", False, False
