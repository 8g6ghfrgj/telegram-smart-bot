# bot/keyboards.py
# =========================
# جميع أزرار البوت (Inline Keyboards)
# =========================

from telegram import InlineKeyboardMarkup, InlineKeyboardButton


# ======================
# Main Menu
# ======================

def main_menu_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("👥 إدارة الحسابات", callback_data="manage_sessions")],
            [InlineKeyboardButton("📂 رفع روابط", callback_data="upload_links")],
            [InlineKeyboardButton("🧹 تصفية الروابط", callback_data="filter_links")],
            [InlineKeyboardButton("📤 توزيع الروابط", callback_data="distribute_links")],
            [InlineKeyboardButton("🚀 بدء الانضمام", callback_data="start_join")],
        ]
    )


# ======================
# Sessions Management
# ======================

def sessions_management_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ إضافة حساب", callback_data="add_session")],
            [InlineKeyboardButton("📋 عرض الحسابات", callback_data="list_sessions")],
            [InlineKeyboardButton("❌ حذف حساب", callback_data="remove_session")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")],
        ]
    )


# ======================
# Back Only
# ======================

def back_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")]
        ]
    )
