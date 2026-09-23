from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb
from bot.states.forms import AdminBroadcast
from bot.config import settings

router = Router()


async def check_admin(user_id: int) -> bool:
    """چک کردن ادمین بودن از دیتابیس + لیست تنظیمات"""
    # اول از لیست تنظیمات چک کن
    admin_ids = getattr(settings, "ADMIN_IDS", [])
    if isinstance(admin_ids, list) and user_id in admin_ids:
        return True
    
    # بعد از دیتابیس چک کن
    user = await q.get_user(user_id)
    if not user:
        return False
    
    # هر مقدار حقیقت‌مانند را قبول کن (1, True, "1" و ...)
    return bool(user.get("is_admin"))


@router.callback_query(F.data == "menu:admin")
async def admin_menu(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        await callback.answer("دسترسی نداری!", show_alert=True)
        return
    
    total_users = await q.count_users()
    
    text = (
        f"👑 <b>پنل ادمین</b>\n\n"
        f"👥 تعداد کل کاربران: <b>{total_users}</b>\n\n"
        "از دکمه‌های زیر استفاده کن:"
    )
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 پیام گروهی", callback_data="admin:broadcast"))
    builder.row(InlineKeyboardButton(text="📊 آمار کلی", callback_data="admin:stats"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        await callback.answer("دسترسی نداری!", show_alert=True)
        return
    await state.set_state(AdminBroadcast.message)
    await callback.message.edit_text(
        "📢 پیام گروهی رو بنویس:\n"
        "(این پیام برای همه کاربران ارسال می‌شه)"
    )
    await callback.answer()


@router.message(AdminBroadcast.message)
async def broadcast_send(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return
    
    users = await q.get_all_users()
    success = 0
    failed = 0
    
    for u in users:
        try:
            await message.bot.send_message(
                u["user_id"], 
                f"📢 <b>پیام از ادمین:</b>\n\n{message.text}",
                parse_mode="HTML"
            )
            success += 1
        except:
            failed += 1
    
    await state.clear()
    await message.answer(
        f"✅ پیام گروهی ارسال شد.\n"
        f"موفق: {success}\n"
        f"ناموفق: {failed}",
        reply_markup=back_to_main_kb()
    )


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        await callback.answer("دسترسی نداری!", show_alert=True)
        return
    
    total = await q.count_users()
    
    text = (
        f"📊 <b>آمار کلی ربات</b>\n\n"
        f"👥 تعداد کل کاربران: <b>{total}</b>\n"
    )
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()
