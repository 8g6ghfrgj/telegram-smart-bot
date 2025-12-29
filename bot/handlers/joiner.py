# bot/handlers/joiner.py
# =========================
# توزيع الروابط + الانضمام التلقائي (Background)
# =========================

import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from database.models import SessionModel, LinkModel, AssignmentModel
from tgclient.manager import telethon_manager
from bot.keyboards import back_keyboard
from config import LINKS_PER_SESSION, JOIN_DELAY_SECONDS


# ======================
# Callback: توزيع الروابط
# ======================

async def distribute_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: توزيع الروابط على الحسابات
    """
    query = update.callback_query
    await query.answer()

    sessions = SessionModel.get_active()
    if not sessions:
        await query.edit_message_text(
            "❌ لا توجد حسابات للتوزيع.",
            reply_markup=back_keyboard(),
        )
        return

    links = LinkModel.get_alive_unassigned()
    if not links:
        await query.edit_message_text(
            "❌ لا توجد روابط جاهزة للتوزيع.\n"
            "تأكد من رفع الروابط ثم تصفيتها.",
            reply_markup=back_keyboard(),
        )
        return

    link_index = 0
    assigned = 0

    for session in sessions:
        for _ in range(LINKS_PER_SESSION):
            if link_index >= len(links):
                break

            AssignmentModel.assign(
                session_id=session["id"],
                link_id=links[link_index]["id"],
            )
            assigned += 1
            link_index += 1

        if link_index >= len(links):
            break

    await query.edit_message_text(
        f"✅ تم توزيع {assigned} رابط على الحسابات.",
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

    # نمنع تشغيله مرتين
    if context.application.bot_data.get("joiner_running"):
        await query.edit_message_text(
            "⚠️ الانضمام يعمل بالفعل.",
            reply_markup=back_keyboard(),
        )
        return

    context.application.bot_data["joiner_running"] = True
    asyncio.create_task(_join_loop())

    await query.edit_message_text(
        "🚀 تم بدء الانضمام التلقائي.\n"
        "سيستمر العمل في الخلفية.",
        reply_markup=back_keyboard(),
    )


# ======================
# Background Join Loop
# ======================

async def _join_loop():
    """
    حلقة الانضمام المستمرة
    لا تتوقف
    """
    while True:
        sessions = SessionModel.get_active()

        for session in sessions:
            pending = AssignmentModel.get_pending_by_session(session["id"])
            if not pending:
                continue

            try:
                client = await telethon_manager.get_client(
                    session["id"],
                    session["session_string"],
                )
            except Exception:
                continue

            for item in pending:
                link = item["link"]
                link_id = item["link_id"]

                try:
                    # Telethon يتعامل مع العام والخاص تلقائيًا
                    await client.join_chat(link)

                    AssignmentModel.mark_joined(
                        session_id=session["id"],
                        link_id=link_id,
                    )

                    await asyncio.sleep(JOIN_DELAY_SECONDS)

                except Exception:
                    # نتجاهل الخطأ ونكمل
                    await asyncio.sleep(JOIN_DELAY_SECONDS)
                    continue

        # فاصل بسيط قبل الدورة التالية
        await asyncio.sleep(5)
