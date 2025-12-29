# bot/handlers/links_input.py
# =========================
# إدخال روابط تيليجرام (نص أو ملف txt)
# مربوط مع core/link_extractor
# =========================

from telegram import Update
from telegram.ext import ContextTypes

from database.models import LinkModel
from bot.keyboards import back_keyboard

from core.link_extractor import (
    extract_links,
    extract_links_from_file_bytes,
)


# ======================
# Callback Button
# ======================

async def upload_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر: رفع روابط
    """
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data["awaiting_links"] = True

    await query.edit_message_text(
        "📂 أرسل الروابط الآن (نص مباشر أو ملف txt):",
        reply_markup=back_keyboard(),
    )


# ======================
# Text / File Handler
# ======================

async def handle_links_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    استقبال الروابط كنص أو ملف
    """
    if not context.user_data.get("awaiting_links"):
        return

    context.user_data.clear()

    links = []

    # --------
    # ملف txt
    # --------
    if update.message.document:
        file = await update.message.document.get_file()
        data = await file.download_as_bytearray()
        links = extract_links_from_file_bytes(data)

    # --------
    # نص مباشر
    # --------
    elif update.message.text:
        links = extract_links(update.message.text)

    if not links:
        await update.message.reply_text(
            "❌ لم يتم العثور على روابط تيليجرام.",
            reply_markup=back_keyboard(),
        )
        return

    added = 0
    for link in links:
        if LinkModel.add(link):
            added += 1

    await update.message.reply_text(
        f"✅ تم حفظ {added} رابط.",
        reply_markup=back_keyboard(),
    )
