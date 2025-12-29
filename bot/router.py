# bot/router.py
# Router مركزي لكل الأوامر والأزرار
# يمنع تعارض CallbackQueryHandlers نهائيًا

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# start
from bot.handlers.start import start_command

# sessions
from bot.handlers.sessions import (
    add_session_callback,
    list_sessions_callback,
    remove_session_callback,
    handle_text as sessions_text_handler,
)

# links
from bot.handlers.links_input import (
    upload_links_callback,
    handle_links_text,
)

# filters
from bot.handlers.filters import filter_links_callback

# distribution / join
from bot.handlers.joiner import (
    distribute_links_callback,
    start_join_callback,
)


def register_all_handlers(app):
    """
    تسجيل جميع الهاندلرز بترتيب صحيح
    """

    # ==========
    # Commands
    # ==========
    app.add_handler(CommandHandler("start", start_command))

    # ======================
    # CallbackQuery (Buttons)
    # ======================

    # Sessions
    app.add_handler(
        CallbackQueryHandler(add_session_callback, pattern="^add_session$")
    )
    app.add_handler(
        CallbackQueryHandler(list_sessions_callback, pattern="^list_sessions$")
    )
    app.add_handler(
        CallbackQueryHandler(remove_session_callback, pattern="^remove_session$")
    )

    # Links
    app.add_handler(
        CallbackQueryHandler(upload_links_callback, pattern="^upload_links$")
    )

    # Filters
    app.add_handler(
        CallbackQueryHandler(filter_links_callback, pattern="^filter_links$")
    )

    # Distribution / Join
    app.add_handler(
        CallbackQueryHandler(distribute_links_callback, pattern="^distribute_links$")
    )
    app.add_handler(
        CallbackQueryHandler(start_join_callback, pattern="^start_join$")
    )

    # ======================
    # Text input (ONE handler only)
    # ======================

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            _text_router,
        )
    )


# ======================
# Internal text router
# ======================

async def _text_router(update, context):
    """
    Router للنصوص حسب الحالة
    يمنع تعارض MessageHandlers
    """

    # جلسات
    if context.user_data.get("awaiting_session"):
        return await sessions_text_handler(update, context)

    # روابط
    if context.user_data.get("awaiting_links"):
        return await handle_links_text(update, context)

    # أي نص غير متوقع
    await update.message.reply_text(
        "❌ الأمر غير متوقع. استخدم القائمة."
    )
