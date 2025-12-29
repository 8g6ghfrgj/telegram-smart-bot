# bot/handlers/sessions.py
# إدارة جلسات Telethon (إضافة / عرض / حذف)
# يعتمد على telethon/manager.py و database/models.py و keyboards

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler

from telethon.manager import telethon_manager
from database.models import SessionModel
from bot.keyboards import back_keyboard


async def add_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر إضافة جلسة
    """
    query = update.callback_query
    await query.answer()

    context.user_data["awaiting_session"] = True

    await query.edit_message_text(
        "➕ أرسل الآن StringSession الخاصة بالحساب:",
        reply_markup=back_keyboard(),
    )


async def handle_session_string(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    استقبال StringSession
    """
    if not context.user_data.get("awaiting_session"):
        return

    session_string = update.message.text.strip()
    context.user_data["awaiting_session"] = False

    success = telethon_manager.add_session(session_string)

    if success:
        await update.message.reply_text(
            "✅ تم إضافة الحساب بنجاح.",
            reply_markup=back_keyboard(),
        )
    else:
        await update.message.reply_text(
            "❌ فشل إضافة الحساب (مكرر أو تم الوصول للحد الأقصى).",
            reply_markup=back_keyboard(),
        )


async def list_sessions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    عرض الحسابات
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

    text = "👥 الحسابات النشطة:\n\n"
    for s in sessions:
        text += f"- ID: {s['id']}\n"

    await query.edit_message_text(text, reply_markup=back_keyboard())


async def remove_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    طلب حذف حساب
    """
    query = update.callback_query
    await query.answer()

    context.user_data["awaiting_remove_session"] = True

    await query.edit_message_text(
        "❌ أرسل ID الحساب المراد حذفه:",
        reply_markup=back_keyboard(),
    )


async def handle_remove_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    تنفيذ حذف الحساب
    """
    if not context.user_data.get("awaiting_remove_session"):
        return

    context.user_data["awaiting_remove_session"] = False

    try:
        session_id = int(update.message.text.strip())
        telethon_manager.deactivate_session(session_id)

        await update.message.reply_text(
            "✅ تم حذف الحساب.",
            reply_markup=back_keyboard(),
        )
    except Exception:
        await update.message.reply_text(
            "❌ ID غير صحيح.",
            reply_markup=back_keyboard(),
        )


def register_sessions_handlers(app):
    """
    تسجيل الهاندلرز
    """
    app.add_handler(CallbackQueryHandler(add_session_callback, pattern="^add_session$"))
    app.add_handler(CallbackQueryHandler(list_sessions_callback, pattern="^list_sessions$"))
    app.add_handler(CallbackQueryHandler(remove_session_callback, pattern="^remove_session$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_session_string))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_remove_session))
