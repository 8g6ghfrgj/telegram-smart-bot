# bot/handlers/joiner.py
# تشغيل الانضمام التلقائي وتوزيع الروابط
# يعتمد على core/distributor.py و core/scheduler.py

import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from core.distributor import distribute_links
from core.scheduler import run_join_scheduler
from bot.keyboards import back_keyboard


async def distribute_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر توزيع الروابط على الحسابات
    """
    query = update.callback_query
    await query.answer()

    distribution = distribute_links()

    if not distribution:
        await query.edit_message_text(
            "❌ لا توجد روابط أو حسابات للتوزيع.",
            reply_markup=back_keyboard(),
        )
        return

    total = sum(len(v) for v in distribution.values())

    await query.edit_message_text(
        f"✅ تم توزيع {total} رابط على الحسابات.",
        reply_markup=back_keyboard(),
    )


async def start_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر بدء الانضمام التلقائي
    """
    query = update.callback_query
    await query.answer()

    # تشغيل الجدولة في الخلفية مرة واحدة فقط
    if not context.application.bot_data.get("join_scheduler_started"):
        context.application.bot_data["join_scheduler_started"] = True
        asyncio.create_task(run_join_scheduler())

    await query.edit_message_text(
        "🚀 تم تشغيل الانضمام التلقائي.\n"
        "ال
