# core/classifier.py
# تصنيف روابط تيليجرام تصنيفًا مبدئيًا قبل الفحص الحقيقي عبر Telethon
# هذا الملف لا يعتمد على Telethon إطلاقًا

from typing import Literal

Category = Literal[
    "bot",
    "channel",
    "group_public",
    "group_private",
    "message_link",
    "unknown"
]


def classify_link(link: str) -> Category:
    """
    تصنيف أولي اعتمادًا على شكل الرابط فقط
    """

    l = link.lower().strip()

    # روابط البوتات
    if l.endswith("bot") or "bot?" in l:
        return "bot"

    # روابط الرسائل داخل مجموعات أو قنوات
    # مثال: https://t.me/c/123456/789
    if "/c/" in l:
        return "message_link"

    # روابط الانضمام الخاصة
    # مثال: https://t.me/+xxxx أو joinchat
    if "/+" in l or "joinchat" in l:
        return "group_private"

    # روابط عامة (قد تكون قناة أو مجموعة)
    # التمييز النهائي يتم لاحقًا عبر Telethon
    if l.startswith("https://t.me/"):
        return "channel"

    return "unknown"


def is_joinable_category(category: Category) -> bool:
    """
    هل هذا النوع قابل للانضمام؟
    """
    return category in ("channel", "group_public", "group_private")
