from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb
from bot.utils.jalali import today_jalali, jalali_to_display
from bot.services.scoring import calculate_system_score

router = Router()


@router.callback_query(F.data == "menu:profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await q.get_user(user_id)
    if not user:
        await callback.answer("ابتدا /start بزنید", show_alert=True)
        return

    # آمار سریع امروز
    logs = await q.get_activity_logs(user_id)
    total_min = sum(l.get("duration_minutes", 0) or 0 for l in logs)
    journal = await q.get_journal(user_id)
    score_data = await q.get_daily_score(user_id)
    
    system_score = score_data.get("system_score") if score_data else "—"
    user_score = score_data.get("user_score") if score_data else "—"

    text = (
        f"🏠 <b>پنل کاربری</b>\n\n"
        f"👤 نام: <b>{user.get('full_name') or callback.from_user.full_name}</b>\n"
        f"🆔 آیدی: <code>{user_id}</code>\n"
        f"📅 عضویت: {jalali_to_display(user.get('join_date', '—'))}\n"
        f"📆 امروز: {jalali_to_display(today_jalali())}\n\n"
        f"📊 <b>آمار امروز</b>\n"
        f"• فعالیت‌های ثبت‌شده: {len(logs)}\n"
        f"• مجموع زمان: {total_min} دقیقه\n"
        f"• ژورنال: {'✅ پر شده' if journal else '❌ خالی'}\n"
        f"• امتیاز تو: {user_score} | سیستم: {system_score}\n\n"
        f"از منوی اصلی بخش‌های مختلف رو مدیریت کن."
    )
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()
