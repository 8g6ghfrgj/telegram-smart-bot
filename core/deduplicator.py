# core/deduplicator.py
# توحيد وحذف تكرار روابط الرسائل المؤدية لنفس المجموعة أو القناة

from typing import Set


def normalize_message_link(link: str) -> str:
    """
    تحويل رابط رسالة إلى رابط الجذر (المجموعة / القناة)
    مثال:
    https://t.me/c/123456/789  -> https://t.me/c/123456
    """
    if "/c/" in link:
        parts = link.split("/")
        try:
            idx = parts.index("c")
            return "/".join(parts[: idx + 2])
        except ValueError:
            return link
    return link


def deduplicate_links(links: Set[str]) -> Set[str]:
    """
    إزالة روابط الرسائل المكررة والإبقاء على رابط واحد فقط
    """
    seen = {}
    for link in links:
        key = normalize_message_link(link)
        if key not in seen:
            seen[key] = link

    return set(seen.values())
