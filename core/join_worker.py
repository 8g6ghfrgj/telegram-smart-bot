# core/join_worker.py
# =========================
# Worker الانضمام التلقائي
# منطق فقط (Background, Never Stop)
# =========================

import asyncio
from typing import List

from telethon.errors import (
    FloodWaitError,
    UserAlreadyParticipantError,
    InviteRequestSentError,
)
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest

from database.models import SessionModel, AssignmentModel
from tgclient.manager import telethon_manager
from config import JOIN_DELAY_SECONDS, NEVER_STOP_JOINING


async def run_join_worker(poll_interval: int = 5):
    """
    حلقة تشغيل دائمة:
    - تجلب الجلسات النشطة
    - تنفّذ الانضمام للروابط الموزعة
    - لا تتوقف إلا إذا NEVER_STOP_JOINING = False
    """

    while True:
        sessions = SessionModel.get_active()

        tasks = []
        for session in sessions:
            tasks.append(
                asyncio.create_task(
                    _process_single_session(session)
                )
            )

        if tasks:
            await asyncio.gather(*tasks)

        if not NEVER_STOP_JOINING:
            break

        await asyncio.sleep(poll_interval)


async def _process_single_session(session: dict):
    """
    تنفيذ الانضمام لحساب واحد
    session = {id, session_string}
    """

    session_id = session["id"]
    session_string = session["session_string"]

    pending = AssignmentModel.get_pending_by_session(session_id)
    if not pending:
        return

    try:
        client = await telethon_manager.get_client(
            session_id,
            session_string,
        )
    except Exception:
        return

    for item in pending:
        link = item["link"]
        link_id = item["link_id"]

        try:
            # روابط خاصة
            if "joinchat" in link or "/+" in link:
                invite_hash = link.split("/")[-1]
                await client(ImportChatInviteRequest(invite_hash))

            # روابط عامة
            else:
                await client(JoinChannelRequest(link))

            AssignmentModel.mark_joined(session_id, link_id)
            await asyncio.sleep(JOIN_DELAY_SECONDS)

        except UserAlreadyParticipantError:
            AssignmentModel.mark_joined(session_id, link_id)
            continue

        except InviteRequestSentError:
            # تم إرسال طلب انضمام
            AssignmentModel.mark_joined(session_id, link_id)
            continue

        except FloodWaitError as e:
            # احترام FloodWait ثم المتابعة
            await asyncio.sleep(e.seconds)
            continue

        except Exception:
            # تجاهل أي خطأ والاستمرار
            await asyncio.sleep(JOIN_DELAY_SECONDS)
            continue
