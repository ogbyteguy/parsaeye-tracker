from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb, confirm_kb
from bot.states.forms import DailyPlan
from bot.utils.jalali import today_jalali, tomorrow_jalali, jalali_to_display
import json

router = Router()


@router.callback_query(F.data == "menu:daily_plan")
async def daily_plan_menu(callback: CallbackQuery):
    today = today_jalali()
    plan = await q.get_daily_plan(callback.from_user.id, today)
    
    text = f"📅 <b>برنامه روزانه</b>\nامروز: {jalali_to_display(today)}\n\n"
    
    if plan:
        try:
            content = json.loads(plan["content"]) if plan["content"].startswith("[") else plan["content"]
            text += f"برنامه امروز:\n{content if isinstance(content, str) else chr(10).join(content)}\n"
        except:
            text += f"{plan['content']}\n"
    else:
        text += "هنوز برنامه‌ای برای امروز ثبت نشده.\n"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✏️ نوشتن/ویرایش برنامه امروز", callback_data="plan:edit_today"))
    builder.row(InlineKeyboardButton(text="📝 برنامه فردا", callback_data="plan:edit_tomorrow"))
    builder.row(InlineKeyboardButton(text="🔍 مقایسه برنامه vs واقعیت", callback_data="plan:compare"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.in_({"plan:edit_today", "plan:edit_tomorrow"}))
async def edit_plan_start(callback: CallbackQuery, state: FSMContext):
    target = today_jalali() if callback.data == "plan:edit_today" else tomorrow_jalali()
    await state.update_data(plan_date=target)
    await state.set_state(DailyPlan.content)
    await callback.message.edit_text(
        f"برنامه روز {jalali_to_display(target)} رو بنویس.\n"
        "می‌تونی لیست‌وار بنویسی (هر خط یک کار):\n"
        "مثال:\n"
        "- مطالعه ۲ ساعت\n"
        "- باشگاه ۴۵ دقیقه\n"
        "- کار روی پروژه",
        reply_markup=back_to_main_kb()
    )
    await callback.answer()


@router.message(DailyPlan.content)
async def save_plan(message: Message, state: FSMContext):
    data = await state.get_data()
    plan_date = data.get("plan_date", today_jalali())
    content = message.text.strip()
    
    await q.save_daily_plan(message.from_user.id, plan_date, content)
    await state.clear()
    
    await message.answer(
        f"✅ برنامه روز {jalali_to_display(plan_date)} ذخیره شد!\n\n{content}",
        reply_markup=back_to_main_kb()
    )


@router.callback_query(F.data == "plan:compare")
async def compare_plan(callback: CallbackQuery):
    user_id = callback.from_user.id
    today = today_jalali()
    plan = await q.get_daily_plan(user_id, today)
    logs = await q.get_activity_logs(user_id, today)
    
    text = f"🔍 <b>مقایسه برنامه vs واقعیت</b>\n{jalali_to_display(today)}\n\n"
    
    if plan:
        text += f"📋 <b>برنامه:</b>\n{plan['content']}\n\n"
    else:
        text += "📋 برنامه‌ای ثبت نشده بود.\n\n"
    
    text += "⚡ <b>فعالیت‌های واقعی:</b>\n"
    if logs:
        for l in logs:
            name = l.get("act_name") or l.get("activity_name") or "نامشخص"
            mins = l.get("duration_minutes", 0)
            planned = "✅" if l.get("is_planned") else "📌 خارج برنامه"
            text += f"• {name} — {mins} دقیقه {planned}\n"
    else:
        text += "هنوز چیزی ثبت نشده.\n"
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()
