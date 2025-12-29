from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters

from bot.handlers.start import start_command
from bot.handlers.sessions import (
    add_session_callback,
    list_sessions_callback,
    remove_session_callback,
    handle_text,
)
from bot.handlers.links_input import upload_links_callback
from bot.handlers.filters import filter_links_callback
from bot.handlers.joiner import distribute_links_callback, start_join_callback


def register_all_handlers(app):
    app.add_handler(CommandHandler("start", start_command))

    app.add_handler(CallbackQueryHandler(add_session_callback, pattern="^add_session$"))
    app.add_handler(CallbackQueryHandler(list_sessions_callback, pattern="^list_sessions$"))
    app.add_handler(CallbackQueryHandler(remove_session_callback, pattern="^remove_session$"))
    app.add_handler(CallbackQueryHandler(upload_links_callback, pattern="^upload_links$"))
    app.add_handler(CallbackQueryHandler(filter_links_callback, pattern="^filter_links$"))
    app.add_handler(CallbackQueryHandler(distribute_links_callback, pattern="^distribute_links$"))
    app.add_handler(CallbackQueryHandler(start_join_callback, pattern="^start_join$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
