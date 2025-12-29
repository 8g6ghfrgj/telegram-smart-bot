# bot/main.py
# نقطة تشغيل البوت
# هذا الملف يربط كل شيء معًا ولا يحتوي منطق أعمال

import asyncio
import logging

from telegram.ext import (
    Application,
    ApplicationBuilder,
)

from bot.config import BOT_TOKEN
from database.db import init_db

from bot.handlers.start import register_start_handlers
from bot.handlers.links_input import register_links_input_handlers
from bot.handlers.sessions import register_sessions_handlers
from bot.handlers.filters import register_filters_handlers
from bot.handlers.joiner import register_joiner_handlers


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def build_application() -> Application:
    """
    إنشاء تطبيق البوت وتسجيل جميع الهاندلرز
    """
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # handlers
    register_start_handlers(app)
    register_links_input_handlers(app)
    register_sessions_handlers(app)
    register_filters_handlers(app)
    register_joiner_handlers(app)

    return app


async def main():
    """
    التشغيل الرئيسي
    """
    # تهيئة قاعدة البيانات
    init_db()

    # إنشاء وتشغيل البوت
    app = build_application()

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # إبقاء البوت حي
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
