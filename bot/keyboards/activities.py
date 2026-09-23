from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List


def activities_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ فعالیت جدید", callback_data="act:add"),
        InlineKeyboardButton(text="📋 لیست فعالیت‌ها", callback_data="act:list")
    )
    builder.row(
        InlineKeyboardButton(text="⏱️ ثبت زمان امروز", callback_data="act:log"),
        InlineKeyboardButton(text="📌 فعالیت خارج برنامه", callback_data="act:ad_hoc")
    )
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"))
    return builder.as_markup()


def activities_list_kb(activities: List[dict], action_prefix: str = "act:select") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for act in activities:
        emoji = act.get("color_emoji") or "⚡"
        name = act.get("name", "بدون نام")
        builder.row(InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"{action_prefix}:{act['id']}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:activities"))
    return builder.as_markup()


def duration_quick_kb(activity_id: int = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    times = [15, 30, 45, 60, 90, 120]
    row = []
    for t in times:
        data = f"act:duration:{activity_id}:{t}" if activity_id else f"act:duration_adhoc:{t}"
        row.append(InlineKeyboardButton(text=f"{t} دقیقه", callback_data=data))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="✏️ زمان دلخواه", callback_data=f"act:custom_duration:{activity_id or 0}"))
    builder.row(InlineKeyboardButton(text="🔙 انصراف", callback_data="menu:activities"))
    return builder.as_markup()
