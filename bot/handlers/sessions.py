# bot/handlers/sessions.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler

from tgclient.manager import telethon_manager
from database.models import SessionModel
from bot.keyboards import back_keyboard


async def add_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data["awaiting_session"] = True

    await query.edit_message_text(
        "➕ أرسل StringSession:",
        reply_markup=back_keyboard(),
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    استقبال نص مشروط حسب الحالة
    """
    text = update.message.text.strip()

    # إضافة جلسة
    if context.user_data.get("awaiting_session"):
        context.user_data.clear()
        success = telethon_manager.add_session(text)

        await update.message.reply_text(
            "✅ تم إضافة الحساب." if success else "❌ فشل إضافة الحساب.",
            reply_markup=back_keyboard(),
        )
        return

    # حذف جلسة
    if context.user_data.get("awaiting_remove_session"):
        context.user_data.clear()
        try:
            session_id = int(text)
            telethon_manager.deactivate_session(session_id)
            await update.message.reply_text(
                "✅ تم حذف الحساب.",
                reply_markup=back_keyboard(),
            )
        except ValueError:
            await update.message.reply_text(
                "❌ ID غير صحيح.",
                reply_markup=back_keyboard(),
            )
        return


async def list_sessions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    sessions = SessionModel.get_active()
    if not sessions:
        await query.edit_message_text(
            "❌ لا توجد حسابات.",
            reply_markup=back_keyboard(),
        )
        return

    text = "👥 الحسابات:\n\n"
    for s in sessions:
        text += f"- ID: {s['id']}\n"

    await query.edit_message_text(text, reply_markup=back_keyboard())


async def remove_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data["awaiting_remove_session"] = True

    await query.edit_message_text(
        "❌ أرسل ID الحساب:",
        reply_markup=back_keyboard(),
    )


def register_sessions_handlers(app):
    app.add_handler(CallbackQueryHandler(add_session_callback, pattern="^add_session$"))
    app.add_handler(CallbackQueryHandler(list_sessions_callback, pattern="^list_sessions$"))
    app.add_handler(CallbackQueryHandler(remove_session_callback, pattern="^remove_session$"))

    # Handler واحد فقط للنص
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
