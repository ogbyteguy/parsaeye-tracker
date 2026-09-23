from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🏠 پنل کاربری", callback_data="menu:profile"),
        InlineKeyboardButton(text="📅 برنامه روزانه", callback_data="menu:daily_plan")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ فعالیت‌ها", callback_data="menu:activities"),
        InlineKeyboardButton(text="📝 ژورنال", callback_data="menu:journal")
    )
    builder.row(
        InlineKeyboardButton(text="💰 مالی", callback_data="menu:finance"),
        InlineKeyboardButton(text="📚 درس و مطالعه", callback_data="menu:study")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 عادت‌ها", callback_data="menu:habits"),
        InlineKeyboardButton(text="📊 گزارش‌ها", callback_data="menu:reports")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="menu:settings"),
        InlineKeyboardButton(text="❓ راهنما", callback_data="menu:help")
    )
    
    if is_admin:
        builder.row(InlineKeyboardButton(text="👑 پنل ادمین", callback_data="menu:admin"))
    
    return builder.as_markup()


def back_to_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="menu:main"))
    return builder.as_markup()


def confirm_kb(yes_data: str, no_data: str = "menu:main") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ بله", callback_data=yes_data),
        InlineKeyboardButton(text="❌ خیر", callback_data=no_data)
    )
    return builder.as_markup()
