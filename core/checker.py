# core/link_checker.py
# =========================
# فحص روابط تيليجرام (حي / ميت + تصنيف)
# منطق فقط (يُستدعى من handlers أو workers)
# =========================

import asyncio
from typing import Tuple

from telethon.errors import (
    InviteHashExpiredError,
    InviteHashInvalidError,
    ChannelPrivateError,
)
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.functions.channels import GetFullChannelRequest

from database.models import LinkModel


async def check_single_link(client, link_id: int, link: str) -> Tuple[bool, str]:
    """
    فحص رابط واحد باستخدام Telethon client جاهز
    يرجع:
      (is_alive, category)

    category:
      - channel
      - group_public
      - group_private
      - unknown
    """

    try:
        # روابط خاصة (Invite)
        if "joinchat" in link or "/+" in link:
            invite = await client(CheckChatInviteRequest(link))
            if invite.chat:
                return True, "group_private"
            return False, "unknown"

        # روابط عامة
        entity = await client.get_entity(link)
        full = await client(GetFullChannelRequest(entity))

        participants = getattr(full.full_chat, "participants_count", 0)
        if participants > 0:
            if getattr(entity, "broadcast", False):
                return True, "channel"
            return True, "group_public"

        return False, "unknown"

    except (InviteHashExpiredError, InviteHashInvalidError):
        return False, "unknown"

    except ChannelPrivateError:
        # موجود لكنه خاص
        return True, "group_private"

    except Exception:
        return False, "unknown"


async def bulk_check_links(
    client,
    limit: int = 100,
    delay_seconds: int = 2,
) -> int:
    """
    فحص مجموعة روابط غير مفحوصة (is_alive = 0)
    - يستخدم client واحد
    - يحدّث DB مباشرة
    - يرجع عدد الروابط المفحوصة
    """

    unchecked = LinkModel.get_unchecked(limit=limit)
    if not unchecked:
        return 0

    checked = 0
    for item in unchecked:
        try:
            alive, category = await check_single_link(
                client,
                item["id"],
                item["link"],
            )

            if alive:
                LinkModel.mark_alive(item["id"], category)
            else:
                LinkModel.mark_dead(item["id"])

            checked += 1
            await asyncio.sleep(delay_seconds)

        except Exception:
            # أي خطأ غير متوقع → نعتبر الرابط ميت ونكمل
            LinkModel.mark_dead(item["id"])
            await asyncio.sleep(1)
            continue

    return checked
