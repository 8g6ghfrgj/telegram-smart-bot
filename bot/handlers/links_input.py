# bot/handlers/links_input.py
# =========================
# إدخال روابط تيليجرام (نص أو ملف txt)
# =========================

from telegram import Update
from telegram.ext import ContextTypes

from database.models import LinkModel
from bot.keyboards import back_keyboard


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
# Text / File Handler (via Router)
# ======================

async def handle_links_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    استقبال الروابط كنص أو ملف
    (يتم استدعاؤه من Router المركزي فقط)
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
        content = await file.download_as_bytearray()
        text = content.decode(errors="ignore")
        links = _extract_links(text)

    # --------
    # نص مباشر
    # --------
    elif update.message.text:
        links = _extract_links(update.message.text)

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


# ======================
# Helpers
# ======================

def _extract_links(text: str) -> list[str]:
    """
    استخراج روابط تيليجرام من النص
    """
    results = []
    for token in text.split():
        token = token.strip()
        if token.startswith("https://t.me/") or token.startswith("http://t.me/"):
            results.append(token)

    # إزالة التكرار مع الحفاظ على الترتيب
    return list(dict.fromkeys(results))
