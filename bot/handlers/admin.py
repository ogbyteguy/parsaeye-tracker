from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb
from bot.states.forms import AdminBroadcast
from bot.config import settings

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.callback_query(F.data == "menu:admin")
async def admin_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("دسترسی نداری!", show_alert=True)
        return
    
    total_users = await q.count_users()
    
    text = (
        f"👑 <b>پنل ادمین</b>\n\n"
        f"👥 تعداد کل کاربران: {total_users}\n"
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
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminBroadcast.message)
    await callback.message.edit_text("پیام گروهی رو بنویس (برای همه کاربران ارسال می‌شه):")
    await callback.answer()


@router.message(AdminBroadcast.message)
async def broadcast_send(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    users = await q.get_all_users()
    success = 0
    for u in users:
        try:
            await message.bot.send_message(u["user_id"], f"📢 پیام از ادمین:\n\n{message.text}")
            success += 1
        except:
            pass
    await state.clear()
    await message.answer(f"✅ پیام به {success} کاربر ارسال شد.", reply_markup=back_to_main_kb())


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    total = await q.count_users()
    await callback.message.edit_text(
        f"📊 آمار:\nکل کاربران: {total}",
        reply_markup=back_to_main_kb()
    )
    await callback.answer()
