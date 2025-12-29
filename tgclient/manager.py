# tgclient/manager.py
# إدارة جلسات Telethon (StringSession)
# هذه الطبقة مسؤولة فقط عن:
# - تحميل الجلسات من DB
# - إنشاء TelegramClient عند الطلب
# - إعادة استخدام الاتصال ومنع التكرار

import os
import asyncio
from typing import Dict

from telethon import TelegramClient
from telethon.sessions import StringSession

from config import TELETHON_API_ID, TELETHON_API_HASH
from database.models import SessionModel


class TelethonSessionManager:
    def __init__(self):
        # session_id -> TelegramClient
        self._clients: Dict[int, TelegramClient] = {}
        self._lock = asyncio.Lock()

    async def get_client(self, session_id: int, session_string: str) -> TelegramClient:
        """
        إرجاع عميل Telethon متصل وجاهز.
        يعيد استخدام الاتصال إن وُجد.
        """
        async with self._lock:
            if session_id in self._clients:
                client = self._clients[session_id]
                if client.is_connected():
                    return client

            client = TelegramClient(
                StringSession(session_string),
                int(TELETHON_API_ID),
                TELETHON_API_HASH,
            )

            await client.connect()
            self._clients[session_id] = client
            return client

    async def disconnect(self, session_id: int) -> None:
        """
        فصل اتصال جلسة واحدة
        """
        client = self._clients.pop(session_id, None)
        if client:
            try:
                await client.disconnect()
            except Exception:
                pass

    async def disconnect_all(self) -> None:
        """
        فصل جميع الاتصالات (يُستخدم عند الإيقاف)
        """
        for client in self._clients.values():
            try:
                await client.disconnect()
            except Exception:
                pass
        self._clients.clear()

    # =========================
    # DB helpers (اختصار)
    # =========================

    def add_session(self, session_string: str) -> bool:
        """
        إضافة جلسة جديدة إلى DB
        """
        return SessionModel.add(session_string)

    def get_active_sessions(self):
        """
        جلب الجلسات النشطة من DB
        """
        return SessionModel.get_active()

    async def deactivate_session(self, session_id: int):
        """
        تعطيل جلسة (DB + فصل الاتصال)
        """
        SessionModel.deactivate(session_id)
        await self.disconnect(session_id)


# كائن عام يُستخدم في بقية المشروع
telethon_manager = TelethonSessionManager()
