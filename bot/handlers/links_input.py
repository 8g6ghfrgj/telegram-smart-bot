# bot/handlers/links_input.py
# استقبال الروابط من الرسائل أو الملفات وتصنيفها وتخزينها
# يعتمد على extractor / classifier / deduplicator / database

from telegram import Update, Document
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler

from core.extractor import (
    extract_links_from_text,
    extract_links_from_file_content,
)
from core.classifier import classify_link
from core.deduplicator import deduplicate_links
from database.models import LinkModel
from bot.keyboards import back_keyboard


async def upload_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    زر رفع الروابط
    """
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📂 أرسل الروابط الآن:\n"
        "- نص مباشر\n"
        "- أو ملف txt\n\n"
        "سيتم الاستخراج والتصنيف تلقائيًا.",
        reply_markup=back_keyboard(),
    )


async def handle_text_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    استقبال روابط نصية
    """
    text = update.message.text
    links = extract_links_from_text(text)
    await _process_links(update, links)


async def handle_file_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    استقبال ملف روابط
    """
    document: Document = update.message.document
    file = await document.get_file()
    content = await file.download_as_bytearray()
    text = content.decode(errors="ignore")

    links = extract_links_from_file_content(text)
    await _process_links(update, links)


async def _process_links(update: Update, links: set):
    """
    معالجة الروابط:
    - حذف التكرار
    - تصنيف
    - تخزين
    """
    if not links:
        await update.message.reply_text("❌ لم يتم العثور على روابط.")
        return

    links = deduplicate_links(links)

    saved = 0
    for link in links:
        category = classify_link(link)
        LinkModel.add(link, category)
        saved += 1

    await update.message.reply_text(
        f"✅ تم حفظ {saved} رابط بعد الفرز.",
        reply_markup=back_keyboard(),
    )


def register_links_input_handlers(app):
    """
    تسجيل الهاندلرز
    """
    app.add_handler(CallbackQueryHandler(upload_links_callback, pattern="^upload_links$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_links))
    app.add_handler(MessageHandler(filters.Document.TEXT, handle_file_links))
