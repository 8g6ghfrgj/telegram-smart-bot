# core/extractor.py
# استخراج روابط تيليجرام من النصوص والملفات
# هذا الملف مستقل ويُستخدم من handlers و core مباشرة

import re
from typing import Set

from bot.config import TELEGRAM_LINK_REGEX


def extract_links_from_text(text: str) -> Set[str]:
    """
    استخراج جميع روابط تيليجرام من نص واحد
    """
    if not text:
        return set()

    return set(re.findall(TELEGRAM_LINK_REGEX, text))


def extract_links_from_lines(lines: list) -> Set[str]:
    """
    استخراج الروابط من قائمة أسطر (ملفات txt مثلاً)
    """
    links = set()
    for line in lines:
        links.update(extract_links_from_text(line))
    return links


def extract_links_from_file_content(content: str) -> Set[str]:
    """
    محتوى ملف كنص كامل
    """
    return extract_links_from_text(content)
