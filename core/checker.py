# core/checker.py
# فحص روابط تيليجرام (حية / ميتة) وتحديد النوع الحقيقي عبر Telethon
# يعتمد على tgclient/manager.py و database/models.py

import asyncio
from typing import Tuple

from telethon.errors import (
    InviteHashExpiredError,
    InviteHashInvalidError,
    ChannelPrivateError,
)
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.functions.channels import GetFullChannelRequest

from tgclient.manager import telethon_manager
from database.models import LinkModel


async def check_link_alive(
    session_id: int,
    session_string: str,
    link_id: int,
    link: str,
) -> Tuple[bool, str]:
    """
    يفحص الرابط:
    - هل حي أم ميت
    - يحدد التصنيف النهائي
    """

    client = await telethon_manager.get_client(session_id, session_string)

    try:
        # روابط الانضمام الخاصة
        if "joinchat" in link or "/+" in link:
            invite = await client(CheckChatInviteRequest(link))
            if invite.chat:
                return True, "group_private"
            return False, "unknown"

        # روابط عامة
        entity = await client.get_entity(link)
        full = await client(GetFullChannelRequest(entity))

        if getattr(full.full_chat, "participants_count", 0) > 0:
            if getattr(entity, "broadcast", False):
                return True, "channel"
            return True, "group_public"

        return False, "unknown"

    except (InviteHashExpiredError, InviteHashInvalidError):
        LinkModel.mark_dead(link_id)
        return False, "unknown"

    except ChannelPrivateError:
        return True, "group_private"

    except Exception:
        LinkModel.mark_dead(link_id)
        return False, "unknown"


async def bulk_check_links(session: dict, links: list):
    """
    فحص مجموعة روابط باستخدام حساب واحد
    """

    for item in links:
        try:
            await check_link_alive(
                session["id"],
                session["session_string"],
                item["id"],
                item["link"],
            )
            await asyncio.sleep(2)
        except Exception:
            continue
