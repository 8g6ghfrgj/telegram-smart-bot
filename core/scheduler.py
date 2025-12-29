# core/scheduler.py
# جدولة وتنفيذ الانضمام التلقائي بدون توقف
# هذا الملف يعتمد على telethon/join.py و database/models.py و bot/config.py

import asyncio
from typing import Dict, List

from database.models import AssignmentModel, SessionModel
from tgclient.join import join_links_for_session
from bot.config import NEVER_STOP_JOINING


async def run_join_scheduler():
    """
    حلقة تشغيل دائمة:
    - تجلب الجلسات النشطة
    - لكل جلسة تنفذ الانضمام للروابط الموزعة عليها
    - لا تتوقف نهائيًا
    """

    while True:
        sessions = SessionModel.get_active()

        tasks = []
        for session in sessions:
            tasks.append(
                asyncio.create_task(
                    process_session(session)
                )
            )

        if tasks:
            await asyncio.gather(*tasks)

        # إعادة المحاولة دائمًا
        if not NEVER_STOP_JOINING:
            break

        await asyncio.sleep(10)


async def process_session(session: dict):
    """
    تنفيذ الانضمام لجلسة واحدة
    """
    session_id = session["id"]
    pending_links = AssignmentModel.get_pending_by_session(session_id)

    if not pending_links:
        return

    links = [item["link"] for item in pending_links]
    await join_links_for_session(session, links)
