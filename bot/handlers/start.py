# bot/handlers/start.py
# معالج أمر /start والتنقل الأساسي
# يعتمد على keyboards فقط

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.keyboards import main_menu_keyboard, sessions_management_keyboard


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start
    """
    if update.message:
        await update.message.reply_text(
            "🤖 بوت إدارة وفرز روابط تيليجرام\nاختر من القائمة:",
            reply_markup=main_menu_keyboard(),
        )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    التنقل بين القوائم
    """
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_main":
        await query.edit_message_text(
            "🤖 القائمة الرئيسية:",
            reply_markup=main_menu_keyboard(),
        )

    elif data == "manage_sessions":
        await query.edit_message_text(
            "👥 إدارة الحسابات:",
            reply_markup=sessions_management_keyboard(),
        )


def register_start_handlers(app):
    """
    تسجيل الهاندلرز
    """
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(menu_callback))
