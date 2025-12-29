# config.py
# الإعدادات العامة للبوت (مصدر الحقيقة)

import os

# =========================
# Telegram Bot
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN غير مضبوط في المتغيرات البيئية")

# =========================
# Telethon
# =========================

TELETHON_API_ID = os.getenv("TELETHON_API_ID")
TELETHON_API_HASH = os.getenv("TELETHON_API_HASH")

# Telethon مطلوب فقط عند تشغيل خدمات الانضمام
REQUIRE_TELETHON = True

# =========================
# Database
# =========================

DB_PATH = os.getenv("DB_PATH", "data/bot.db")

# =========================
# Sessions / Accounts
# =========================

MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "50"))

# =========================
# Links / Distribution
# =========================

# أقصى عدد روابط لكل حساب في التوزيع الواحد
LINKS_PER_SESSION = int(os.getenv("LINKS_PER_SESSION", "500"))

# تأخير بين كل انضمام (ثواني)
JOIN_DELAY_SECONDS = int(os.getenv("JOIN_DELAY_SECONDS", "60"))

# =========================
# Scheduler / Joiner
# =========================

# عدم التوقف عن المحاولة مهما حصل
NEVER_STOP_JOINING = os.getenv("NEVER_STOP_JOINING", "true").lower() == "true"

# في حال خطأ غير متوقع أثناء الانضمام
SKIP_ON_ERROR = os.getenv("SKIP_ON_ERROR", "true").lower() == "true"

# =========================
# Logging
# =========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =========================
# Validation
# =========================

if REQUIRE_TELETHON:
    if not TELETHON_API_ID or not TELETHON_API_HASH:
        raise RuntimeError(
            "TELETHON_API_ID و TELETHON_API_HASH غير مضبوطين في المتغيرات البيئية"
        )
