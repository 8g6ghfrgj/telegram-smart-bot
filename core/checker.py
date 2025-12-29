# core/checker.py
# فحص روابط تيليجرام (حية / ميتة) وتحديد النوع الحقيقي عبر Telethon
# هذا الملف يعتمد على telethon/manager.py و database/models.py

import asyncio
from typing import Tuple

from telethon.errors import (
    InviteHashExpiredError,
    InviteHashInvalidError,
    ChannelPrivateError,
)
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.functions.channels import GetFullChannelRequest

from telethon.manager import telethon_manager
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
    - يحدد التصنيف النهائي:
      channel / group_public / group_private

    يرجع:
    (is_alive, final_category)
    """

    client = await telethon_manager.get_client(session_id, session_string)

    try:
        # روابط الانضمام الخاصة
        if "joinchat" in link or "/+" in link:
            invite = await client(CheckChatInviteRequest(link))
            if invite.chat:
                return True, "group_private"
            return False, "unknown"

        # روابط عامة (قناة أو مجموعة)
        entity = await client.get_entity(link)
        full = await client(GetFullChannelRequest(entity))

        if getattr(full.full_chat, "participants_count", 0) > 0:
            if entity.broadcast:
                return True, "channel"
            else:
                return True, "group_public"

        return False, "unknown"

    except (InviteHashExpiredError, InviteHashInvalidError):
        LinkModel.mark_dead(link_id)
        return False, "unknown"

    except ChannelPrivateError:
        # قناة/مجموعة خاصة لكنها موجودة
        return True, "group_private"

    except Exception:
        LinkModel.mark_dead(link_id)
        return False, "unknown"


async def bulk_check_links(
    session: dict,
    links: list,
):
    """
    فحص مجموعة روابط باستخدام حساب واحد
    session = {id, session_string}
    links = [{id, link}]
    """

    for item in links:
        try:
            alive, category = await check_link_alive(
                session["id"],
                session["session_string"],
                item["id"],
                item["link"],
            )

            if alive:
                LinkModel.mark_assigned(item["id"])
            else:
                LinkModel.mark_dead(item["id"])

            await asyncio.sleep(2)

        except Exception:
            continue
