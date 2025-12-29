# config.py
# =========================
# الإعدادات العامة للبوت
# هذا الملف هو مصدر الحقيقة الوحيد
# =========================

import os

# =========================
# Telegram Bot
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN غير مضبوط في المتغيرات البيئية")

# =========================
# Telethon (Accounts)
# =========================

TELETHON_API_ID = os.getenv("TELETHON_API_ID")
TELETHON_API_HASH = os.getenv("TELETHON_API_HASH")

if not TELETHON_API_ID or not TELETHON_API_HASH:
    raise RuntimeError(
        "❌ TELETHON_API_ID أو TELETHON_API_HASH غير مضبوطين"
    )

# =========================
# Database
# =========================

DB_PATH = os.getenv("DB_PATH", "data/bot.db")

# =========================
# Sessions / Accounts
# =========================

# الحد الأقصى للحسابات المضافة
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "50"))

# =========================
# Links / Distribution
# =========================

# عدد الروابط لكل حساب
LINKS_PER_SESSION = int(os.getenv("LINKS_PER_SESSION", "500"))

# =========================
# Join / Scheduler
# =========================

# تأخير بين كل انضمام (بالثواني)
JOIN_DELAY_SECONDS = int(os.getenv("JOIN_DELAY_SECONDS", "60"))

# عدم التوقف مهما حصل
NEVER_STOP_JOINING = os.getenv("NEVER_STOP_JOINING", "true").lower() == "true"

# تجاهل الأخطاء والاستمرار
SKIP_ON_ERROR = os.getenv("SKIP_ON_ERROR", "true").lower() == "true"

# =========================
# Logging
# =========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
