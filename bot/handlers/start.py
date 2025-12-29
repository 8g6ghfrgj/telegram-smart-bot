# bot/handlers/start.py
# =========================
# /start + التنقل بين القوائم
# =========================

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards import main_menu_keyboard, sessions_management_keyboard


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    أمر /start
    """
    if update.message:
        await update.message.reply_text(
            "🤖 مرحبًا بك في بوت إدارة روابط تيليجرام\n\nاختر من القائمة:",
            reply_markup=main_menu_keyboard(),
        )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    التنقل بين:
    - القائمة الرئيسية
    - إدارة الحسابات
    """
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "manage_sessions":
        await query.edit_message_text(
            "👥 إدارة الحسابات:",
            reply_markup=sessions_management_keyboard(),
        )

    elif data == "back_main":
        await query.edit_message_text(
            "🤖 القائمة الرئيسية:",
            reply_markup=main_menu_keyboard(),
        )
