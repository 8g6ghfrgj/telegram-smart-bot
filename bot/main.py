# bot/main.py
# نقطة تشغيل البوت (النسخة الصحيحة لـ python-telegram-bot v20)

import logging
from telegram.ext import ApplicationBuilder

from bot.config import BOT_TOKEN
from database.db import init_db
from bot.router import register_all_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main():
    # تهيئة قاعدة البيانات
    init_db()

    # إنشاء التطبيق
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # تسجيل جميع الهاندلرز من Router واحد
    register_all_handlers(app)

    # تشغيل البوت (Polling صحيح)
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
