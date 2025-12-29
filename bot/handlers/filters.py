# bot/handlers/filters.py
# =========================
# تصفية روابط تيليجرام
# مربوط مع core/link_checker
# =========================

from telegram import Update
from telegram.ext import ContextTypes

from tgclient.manager import telethon_manager
from database.models import SessionModel
from bot.keyboards import back_keyboard

from core.link_checker import bulk_check_links


# ======================
# Callback Button
# ======================

async def filter_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: تصفية الروابط
    """
    query = update.callback_query
    await query.answer()

    sessions = SessionModel.get_active()
    if not sessions:
        await query.edit_message_text(
            "❌ لا توجد حسابات لفحص الروابط.",
            reply_markup=back_keyboard(),
        )
        return

    # نستخدم أول حساب فقط للفحص
    session = sessions[0]

    await query.edit_message_text(
        "🧹 جارِ تصفية الروابط...\n"
        "قد يستغرق هذا بعض الوقت.",
        reply_markup=back_keyboard(),
    )

    try:
        client = await telethon_manager.get_client(
            session["id"],
            session["session_string"],
        )
    except Exception:
        await query.edit_message_text(
            "❌ فشل الاتصال بالحساب.",
            reply_markup=back_keyboard(),
        )
        return

    checked = await bulk_check_links(client)

    await query.edit_message_text(
        f"✅ انتهت التصفية.\nتم فحص {checked} رابط.",
        reply_markup=back_keyboard(),
    )
