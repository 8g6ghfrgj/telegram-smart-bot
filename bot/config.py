# bot/config.py
# الإعدادات العامة للمشروع
# هذا الملف ثابت ولن يتم تعديله لاحقًا

import os
from pathlib import Path

# =========================
# المسارات الأساسية
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

BOT_DIR = BASE_DIR / "bot"
CORE_DIR = BASE_DIR / "core"
DB_DIR = BASE_DIR / "database"
TELETHON_DIR = BASE_DIR / "telethon"
OUTPUT_DIR = BASE_DIR / "output"

# إنشاء مجلدات الإخراج إذا لم تكن موجودة
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# إعدادات البوت
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")  # يجب ضبطه في Render Environment
BOT_NAME = "Telegram Smart Bot"

# =========================
# إعدادات Telethon
# =========================

# لا نستخدم API_ID و API_HASH
# الجلسات ستكون StringSession فقط
MAX_SESSIONS = 50
JOIN_DELAY_SECONDS = 60
MAX_LINKS_PER_ACCOUNT = 500

# =========================
# إعدادات قاعدة البيانات
# =========================

DB_PATH = DB_DIR / "bot.db"

# =========================
# إعدادات استخراج الروابط
# =========================

TELEGRAM_LINK_REGEX = r"(https?://t\.me/[^\s]+)"

# =========================
# ملفات الإخراج
# =========================

OUTPUT_FILES = {
    "bots": OUTPUT_DIR / "bots.txt",
    "channels": OUTPUT_DIR / "channels.txt",
    "groups_public": OUTPUT_DIR / "groups_public.txt",
    "groups_private": OUTPUT_DIR / "groups_private.txt",
    "messages": OUTPUT_DIR / "messages_links.txt",
}

# =========================
# إعدادات السلوك الذكي
# =========================

AUTO_RETRY_JOIN = True
SKIP_ON_ERROR = True
NEVER_STOP_JOINING = True

# =========================
# تحقق أساسي
# =========================

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN غير موجود. قم بإضافته كمتغير بيئة.")
