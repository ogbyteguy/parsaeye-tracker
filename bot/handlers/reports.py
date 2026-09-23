from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb
from bot.utils.jalali import today_jalali, jalali_to_display, get_week_range, get_month_range
from bot.services.scoring import calculate_system_score

router = Router()


@router.callback_query(F.data == "menu:reports")
async def reports_menu(callback: CallbackQuery):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 گزارش امروز", callback_data="report:daily"))
    builder.row(InlineKeyboardButton(text="📅 گزارش هفتگی", callback_data="report:weekly"))
    builder.row(InlineKeyboardButton(text="📆 گزارش ماهانه", callback_data="report:monthly"))
    builder.row(InlineKeyboardButton(text="⭐ امتیازدهی دستی امروز", callback_data="report:user_score"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"))
    
    await callback.message.edit_text(
        "📊 <b>گزارش‌ها و امتیازدهی</b>\n\nیکی را انتخاب کن:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "report:daily")
async def daily_report(callback: CallbackQuery):
    user_id = callback.from_user.id
    today = today_jalali()
    user = await q.get_user(user_id)
    name = user.get("full_name") or callback.from_user.first_name
    
    # محاسبه امتیاز سیستم
    score_info = await calculate_system_score(user_id, today)
    score_row = await q.get_daily_score(user_id, today)
    
    logs = await q.get_activity_logs(user_id, today)
    expenses = await q.get_expenses(user_id, date=today)
    journal = await q.get_journal(user_id, today)
    
    text = (
        f"🌟 <b>{name} عزیز، امروز وضعیتت این‌طور بود:</b>\n"
        f"📅 {jalali_to_display(today)}\n\n"
        f"✅ <b>فعالیت‌های انجام‌شده:</b> {len(logs)}\n"
    )
    for l in logs[:5]:
        name_act = l.get("act_name") or l.get("activity_name") or "?"
        text += f"  • {name_act} ({l.get('duration_minutes', 0)} دقیقه)\n"
    
    text += (
        f"\n📊 <b>امتیاز تو:</b> {score_row.get('user_score') if score_row else '—'} | "
        f"<b>امتیاز سیستم:</b> {score_info['system_score']}\n\n"
    )
    
    if expenses:
        total_exp = sum(e["amount"] for e in expenses)
        text += f"💰 <b>خرج‌ها:</b> {total_exp:,.0f} تومان\n"
    
    if journal:
        text += f"📝 <b>ژورنال:</b> پر شده (حالت: {journal.get('mood_score', '—')}/10)\n"
    
    if score_info["strengths"]:
        text += f"\n💪 <b>نقاط قوت:</b>\n" + "\n".join(f"• {s}" for s in score_info["strengths"]) + "\n"
    if score_info["weaknesses"]:
        text += f"\n🔧 <b>پیشنهادها:</b>\n" + "\n".join(f"• {w}" for w in score_info["weaknesses"])
    
    text += "\n\nادامه بده، فردا بهتر می‌شی! 🚀"
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "report:weekly")
async def weekly_report(callback: CallbackQuery):
    start, end = get_week_range()
    scores = await q.get_scores_range(callback.from_user.id, start, end)
    
    text = f"📅 <b>گزارش هفتگی</b>\nاز {jalali_to_display(start)} تا {jalali_to_display(end)}\n\n"
    
    if scores:
        avg_sys = sum(s.get("system_score") or 0 for s in scores) / len(scores)
        text += f"میانگین امتیاز سیستم: {avg_sys:.1f}/10\n"
        text += f"تعداد روزهای ثبت‌شده: {len(scores)}\n"
    else:
        text += "داده‌ای برای این هفته نیست.\n"
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "report:monthly")
async def monthly_report(callback: CallbackQuery):
    start, end = get_month_range()
    scores = await q.get_scores_range(callback.from_user.id, start, end)
    expenses = await q.get_expenses(callback.from_user.id, month=start[:7])
    
    text = f"📆 <b>گزارش ماهانه</b>\n\n"
    if scores:
        avg = sum(s.get("system_score") or 0 for s in scores) / len(scores)
        text += f"میانگین امتیاز: {avg:.1f}\nروزهای فعال: {len(scores)}\n"
    total_exp = sum(e["amount"] for e in expenses)
    text += f"مجموع خرج ماه: {total_exp:,.0f} تومان\n"
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()
