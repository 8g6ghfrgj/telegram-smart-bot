# bot/handlers/joiner.py
# =========================
# التوزيع + بدء الانضمام
# مربوط مع core/distributor و core/join_worker
# =========================

import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards import back_keyboard
from core.distributor import distribute_links
from core.join_worker import run_join_worker


# ======================
# Callback: توزيع الروابط
# ======================

async def distribute_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: توزيع الروابط
    """
    query = update.callback_query
    await query.answer()

    result = distribute_links()

    if result["links"] == 0:
        await query.edit_message_text(
            "❌ لا توجد روابط جاهزة للتوزيع.\n"
            "تأكد من رفع الروابط ثم تصفيتها.",
            reply_markup=back_keyboard(),
        )
        return

    await query.edit_message_text(
        f"✅ تم توزيع {result['links']} رابط على {result['sessions']} حساب.",
        reply_markup=back_keyboard(),
    )


# ======================
# Callback: بدء الانضمام
# ======================

async def start_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: بدء الانضمام التلقائي
    """
    query = update.callback_query
    await query.answer()

    # منع التشغيل المكرر
    if context.application.bot_data.get("join_worker_running"):
        await query.edit_message_text(
            "⚠️ الانضمام يعمل بالفعل.",
            reply_markup=back_keyboard(),
        )
        return

    context.application.bot_data["join_worker_running"] = True

    # تشغيل Worker في الخلفية
    asyncio.create_task(run_join_worker())

    await query.edit_message_text(
        "🚀 تم بدء الانضمام التلقائي.\n"
        "العمل مستمر في الخلفية.",
        reply_markup=back_keyboard(),
    )
