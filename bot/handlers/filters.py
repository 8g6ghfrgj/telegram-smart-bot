# bot/handlers/filters.py
# =========================
# تصفية روابط تيليجرام (حية / ميتة + تصنيف)
# =========================

import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from telethon.errors import (
    InviteHashExpiredError,
    InviteHashInvalidError,
    ChannelPrivateError,
)
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.functions.channels import GetFullChannelRequest

from tgclient.manager import telethon_manager
from database.models import LinkModel, SessionModel
from bot.keyboards import back_keyboard


# ======================
# Callback Button
# ======================

async def filter_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: تصفية الروابط
    """
    query = update.callback_query
    await query.answer()

    sessions = SessionModel.get_active()
    if not sessions:
        await query.edit_message_text(
            "❌ لا توجد حسابات لفحص الروابط.",
            reply_markup=back_keyboard(),
        )
        return

    # نستخدم أول حساب فقط للفحص
    session = sessions[0]

    await query.edit_message_text(
        "🧹 جارِ تصفية الروابط...\nقد يستغرق هذا بعض الوقت.",
        reply_markup=back_keyboard(),
    )

    checked = await _bulk_check_links(session)

    await query.edit_message_text(
        f"✅ انتهت التصفية.\nتم فحص {checked} رابط.",
        reply_markup=back_keyboard(),
    )


# ======================
# Internal Logic
# ======================

async def _bulk_check_links(session: dict, limit: int = 100) -> int:
    """
    فحص مجموعة روابط غير مفحوصة (is_alive = 0)
    """
    unchecked = LinkModel.get_unchecked(limit=limit)
    if not unchecked:
        return 0

    client = await telethon_manager.get_client(
        session["id"], session["session_string"]
    )

    count = 0
    for item in unchecked:
        try:
            alive, category = await _check_single_link(
                client,
                item["id"],
                item["link"],
            )

            if alive:
                LinkModel.mark_alive(item["id"], category)
            else:
                LinkModel.mark_dead(item["id"])

            count += 1
            await asyncio.sleep(2)

        except Exception:
            # أي خطأ غير متوقع → نعتبر الرابط ميت
            LinkModel.mark_dead(item["id"])
            await asyncio.sleep(1)
            continue

    return count


async def _check_single_link(client, link_id: int, link: str):
    """
    فحص رابط واحد
    يرجع: (is_alive: bool, category: str)
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
