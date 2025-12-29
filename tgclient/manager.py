# telethon/manager.py
# إدارة جلسات Telethon (StringSession فقط)
# هذا الملف لا يُنشئ أي اتصال فعلي إلا عند الطلب

import os
import asyncio
from typing import Dict, List, Optional

from telethon import TelegramClient
from telethon.sessions import StringSession

from database.models import SessionModel
from bot.config import MAX_SESSIONS


class TelethonSessionManager:
    """
    مسؤول عن:
    - تحميل الجلسات من قاعدة البيانات
    - إنشاء TelegramClient عند الحاجة فقط
    - منع تكرار الجلسات
    """

    def __init__(self):
        self._clients: Dict[int, TelegramClient] = {}

        # نقرأ القيم هنا لكن لا نستخدمها إلا عند التشغيل الفعلي
        self._api_id = os.getenv("TELETHON_API_ID")
        self._api_hash = os.getenv("TELETHON_API_HASH")

    # =========================
    # Sessions (DB)
    # =========================

    def add_session(self, session_string: str) -> bool:
        """
        إضافة جلسة جديدة إذا لم تتجاوز الحد
        """
        active = SessionModel.get_active()
        if len(active) >= MAX_SESSIONS:
            return False

        if SessionModel.exists(session_string):
            return False

        return SessionModel.add(session_string)

    def get_active_sessions(self) -> List[dict]:
        return SessionModel.get_active()

    def deactivate_session(self, session_id: int):
        SessionModel.deactivate(session_id)
        client = self._clients.pop(session_id, None)
        if client:
            try:
                asyncio.create_task(client.disconnect())
            except Exception:
                pass

    # =========================
    # Telethon Clients
    # =========================

    def _check_credentials(self):
        """
        Telethon يتطلب api_id و api_hash فعليًا.
        لا نمنع التشغيل العام للبوت، لكن نمنع تشغيل الحسابات بدونها.
        """
        if not self._api_id or not self._api_hash:
            raise RuntimeError(
                "TELETHON_API_ID و TELETHON_API_HASH غير مضبوطين في المتغيرات البيئية."
            )

    async def get_client(self, session_id: int, session_string: str) -> TelegramClient:
        """
        إرجاع عميل Telethon جاهز ومتصّل
        """
        if session_id in self._clients:
            return self._clients[session_id]

        self._check_credentials()

        client = TelegramClient(
            StringSession(session_string),
            int(self._api_id),
            self._api_hash
        )

        await client.connect()

        self._clients[session_id] = client
        return client

    async def disconnect_all(self):
        """
        فصل جميع الاتصالات
        """
        for client in self._clients.values():
            try:
                await client.disconnect()
            except Exception:
                pass
        self._clients.clear()


# كائن عام يُستخدم في بقية المشروع
telethon_manager = TelethonSessionManager()
