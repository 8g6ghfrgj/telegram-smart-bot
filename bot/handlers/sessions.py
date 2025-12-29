# bot/handlers/sessions.py
# =========================
# إدارة حسابات Telethon (إضافة / عرض / حذف)
# =========================

from telegram import Update
from telegram.ext import ContextTypes

from tgclient.manager import telethon_manager
from database.models import SessionModel
from bot.keyboards import back_keyboard


# ======================
# Callback Buttons
# ======================

async def add_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: إضافة حساب
    """
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data["awaiting_session"] = True

    await query.edit_message_text(
        "➕ أرسل StringSession الآن:",
        reply_markup=back_keyboard(),
    )


async def list_sessions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: عرض الحسابات
    """
    query = update.callback_query
    await query.answer()

    sessions = SessionModel.get_active()
    if not sessions:
        await query.edit_message_text(
            "❌ لا توجد حسابات مضافة.",
            reply_markup=back_keyboard(),
        )
        return

    lines = ["👥 الحسابات النشطة:\n"]
    for s in sessions:
        lines.append(f"- ID: {s['id']}")

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=back_keyboard(),
    )


async def remove_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: حذف حساب
    """
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data["awaiting_remove_session"] = True

    await query.edit_message_text(
        "❌ أرسل ID الحساب المراد حذفه:",
        reply_markup=back_keyboard(),
    )


# ======================
# Text Handler (via Router)
# ======================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالجة النصوص حسب الحالة فقط
    (يتم استدعاؤها من Router المركزي)
    """
    text = update.message.text.strip()

    # إضافة جلسة
    if context.user_data.get("awaiting_session"):
        context.user_data.clear()
        success = telethon_manager.add_session(text)

        await update.message.reply_text(
            "✅ تم إضافة الحساب بنجاح."
            if success else
            "❌ فشل إضافة الحساب (مكرر أو تجاوز الحد).",
            reply_markup=back_keyboard(),
        )
        return

    # حذف جلسة
    if context.user_data.get("awaiting_remove_session"):
