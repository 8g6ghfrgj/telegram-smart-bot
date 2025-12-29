# bot/keyboards.py
# تعريف جميع أزرار ولوحات التحكم الخاصة بالبوت
# هذا الملف يُستخدم من handlers فقط ولا يحتوي أي منطق

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    القائمة الرئيسية
    """
    keyboard = [
        [
            InlineKeyboardButton("➕ إضافة حساب (Session)", callback_data="add_session"),
        ],
        [
            InlineKeyboardButton("📂 رفع ملف روابط", callback_data="upload_links"),
        ],
        [
            InlineKeyboardButton("🧹 تصفية الروابط الميتة", callback_data="filter_links"),
        ],
        [
            InlineKeyboardButton("🔀 توزيع الروابط", callback_data="distribute_links"),
        ],
        [
            InlineKeyboardButton("🚀 بدء الانضمام التلقائي", callback_data="start_join"),
        ],
        [
            InlineKeyboardButton("👥 إدارة الحسابات", callback_data="manage_sessions"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def sessions_management_keyboard() -> InlineKeyboardMarkup:
    """
    لوحة إدارة الحسابات
    """
    keyboard = [
        [
            InlineKeyboardButton("📋 عرض الحسابات", callback_data="list_sessions"),
        ],
        [
            InlineKeyboardButton("❌ حذف حساب", callback_data="remove_session"),
        ],
        [
            InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_keyboard() -> InlineKeyboardMarkup:
    """
    زر رجوع بسيط
    """
    keyboard = [
        [InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)
