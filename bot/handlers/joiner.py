# bot/handlers/joiner.py
# توزيع الروابط + بدء الانضمام الفعلي
# يعتمد على database/models.py و tgclient/manager.py

import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from database.models import SessionModel, LinkModel, AssignmentModel
from tgclient.manager import telethon_manager
from bot.keyboards import back_keyboard
from config import LINKS_PER_SESSION, JOIN_DELAY_SECONDS


# ======================
# Callback: Distribute
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
# Callback: Start Join
# ======================

async def start_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: بدء الانضمام
    """
    query = update.callback_query
    await query.answer()

    # تشغيل الانضمام في الخلفية مرة واحدة فقط
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
    حلقة الانضمام الدائمة
    """
    while True:
        sessions = SessionModel.get_active()
        for session in sessions:
            pending = AssignmentModel.get_pending_by_session(session["id"])
            if not pending:
                continue

            try:
                client = await telethon_manager.get_client(
                    session["id"], session["session_string"]
                )
            except Exception:
                continue

            for item in pending:
                try:
                    link = item["link"]

                    # روابط خاصة
                    if "joinchat" in link or "/+" in link:
                        await client.join_chat(link)
                    else:
                        await client.join_chat(link)

                    AssignmentModel.mark_joined(
                        session_id=session["id"],
                        link_id=_get_link_id(session["id"], link),
                    )

                    await asyncio.sleep(JOIN_DELAY_SECONDS)

                except Exception:
                    # نتجاهل الخطأ ونكمل
                    await asyncio.sleep(JOIN_DELAY_SECONDS)
                    continue

        # لا نتوقف أبداً
        await asyncio.sleep(5)


def _get_link_id(session_id: int, link: str) -> int:
    """
    جلب link_id من DB
    """
    from database.db import db

    row = db.fetchone(
        """
        SELECT l.id
        FROM links l
        JOIN assignments a ON a.link_id = l.id
        WHERE a.session_id = ? AND l.link = ?
        """,
        (session_id, link),
    )
    return row["id"] if row else 0
