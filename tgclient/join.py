# tgclient/join.py
# تنفيذ الانضمام الفعلي إلى القروبات والقنوات
# يعتمد على tgclient/manager.py و database/models.py و bot/config.py

import asyncio
from typing import List

from telethon.errors import (
    FloodWaitError,
    UserAlreadyParticipantError,
    InviteRequestSentError,
)
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest

from tgclient.manager import telethon_manager
from database.models import AssignmentModel
from bot.config import JOIN_DELAY_SECONDS, SKIP_ON_ERROR


async def join_links_for_session(session: dict, links: List[str]):
    """
    تنفيذ الانضمام إلى الروابط المخصصة لحساب واحد
    session = {id, session_string}
    """

    session_id = session["id"]
    session_string = session["session_string"]

    client = await telethon_manager.get_client(session_id, session_string)

    for link in links:
        try:
            # روابط خاصة
            if "/+" in link or "joinchat" in link:
                invite_hash = link.split("/")[-1]
                await client(ImportChatInviteRequest(invite_hash))

            # روابط عامة
            else:
                await client(JoinChannelRequest(link))

            AssignmentModel.mark_joined(
                session_id,
                _get_link_id(session_id, link),
            )

            await asyncio.sleep(JOIN_DELAY_SECONDS)

        except UserAlreadyParticipantError:
            AssignmentModel.mark_joined(
                session_id,
                _get_link_id(session_id, link),
            )
            continue

        except InviteRequestSentError:
            AssignmentModel.mark_joined(
                session_id,
                _get_link_id(session_id, link),
            )
            continue

        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
            continue

        except Exception:
            if SKIP_ON_ERROR:
                continue
            raise


def _get_link_id(session_id: int, link: str) -> int:
    """
    جلب link_id من قاعدة البيانات
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
