# bot/main.py
# =========================
# نقطة تشغيل البوت (Production)
# متوافق مع python-telegram-bot v20+
# =========================

import logging
from telegram.ext import ApplicationBuilder

from config import BOT_TOKEN
from database.db import init_db
from bot.router import register_all_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main():
    # تهيئة قاعدة البيانات مرة واحدة
    init_db()

    # إنشاء تطبيق البوت
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # تسجيل جميع الهاندلرز عبر Router مركزي
    register_all_handlers(app)

    # تشغيل البوت (Polling صحيح لـ v20)
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
