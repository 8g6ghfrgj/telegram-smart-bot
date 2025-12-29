# core/link_extractor.py
# =========================
# استخراج روابط تيليجرام من نصوص أو ملفات
# منطق فقط (Pure Logic)
# =========================

import re
from typing import List


# نمط روابط تيليجرام (عام + خاص)
TELEGRAM_LINK_REGEX = re.compile(
    r"(https?://t\.me/(?:joinchat/|\+)?[A-Za-z0-9_/-]+)",
    re.IGNORECASE,
)


def extract_links(text: str) -> List[str]:
    """
    استخراج روابط تيليجرام من نص خام
    - يدعم الروابط العامة والخاصة
    - يمنع التكرار
    - يحافظ على الترتيب
    """
    if not text:
        return []

    matches = TELEGRAM_LINK_REGEX.findall(text)
    return _unique_preserve_order(matches)


def extract_links_from_lines(lines: List[str]) -> List[str]:
    """
    استخراج الروابط من قائمة أسطر
    """
    results: List[str] = []
    for line in lines:
        results.extend(extract_links(line))
    return _unique_preserve_order(results)


def extract_links_from_file_bytes(data: bytes) -> List[str]:
    """
    استخراج الروابط من ملف (bytes)
    """
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        return []

    return extract_links(text)


# =========================
# Helpers
# =========================

def _unique_preserve_order(items: List[str]) -> List[str]:
    """
    إزالة التكرار مع الحفاظ على الترتيب
    """
    seen = set()
    result = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
