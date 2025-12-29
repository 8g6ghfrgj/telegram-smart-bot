# bot/handlers/filters.py
# تصفية الروابط الميتة باستخدام حساب واحد متاح
# يعتمد على core/checker.py و database/models.py و telethon/manager.py

import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from core.checker import bulk_check_links
from database.models import LinkModel, SessionModel
from bot.keyboards import back_keyboard


async def filter_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر تصفية الروابط الميتة
    """
    query = update.callback_query
    await query.answer()

    sessions = SessionModel.get_active()
    if not sessions:
        await query.edit_message_text(
            "❌ لا يوجد حسابات لفحص الروابط.",
            reply_markup=back_keyboard(),
        )
        return

    # نستخدم أول حساب فقط للفحص
    session = sessions[0]

    links = LinkModel.get_alive_unassigned()
    if not links:
        await query.edit_message_text(
            "ℹ️ لا توجد روابط لفحصها.",
            reply_markup=back_keyboard(),
        )
        return

    await query.edit_message_text(
        f"🔍 جاري فحص {len(links)} رابط...\n"
        "لن يتم إيقاف العملية.",
        reply_markup=back_keyboard(),
    )

    # تشغيل الفحص في الخلفية
    asyncio.create_task(bulk_check_links(session, links))


def register_filters_handlers(app):
    """
    تسجيل الهاندلرز
    """
    app.add_handler(
        CallbackQueryHandler(filter_links_callback, pattern="^filter_links$")
    )
