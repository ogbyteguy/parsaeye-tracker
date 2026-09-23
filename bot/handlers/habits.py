from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb
from bot.states.forms import HabitForm
from bot.utils.jalali import today_jalali

router = Router()


@router.callback_query(F.data == "menu:habits")
async def habits_menu(callback: CallbackQuery):
    habits = await q.get_habits(callback.from_user.id)
    text = "🔥 <b>عادت‌ساز</b>\n\n"
    
    if habits:
        for h in habits:
            text += f"{h.get('emoji', '🔥')} {h['name']}\n"
    else:
        text += "هنوز عادتی نساختی.\n"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ عادت جدید", callback_data="habit:add"))
    if habits:
        builder.row(InlineKeyboardButton(text="✅ تیک امروز", callback_data="habit:check"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "habit:add")
async def habit_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(HabitForm.name)
    await callback.message.edit_text("نام عادت رو بنویس (مثلاً: مسواک زدن، مطالعه ۳۰ دقیقه):")
    await callback.answer()


@router.message(HabitForm.name)
async def habit_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await q.add_habit(message.from_user.id, name)
    await state.clear()
    await message.answer(f"✅ عادت <b>{name}</b> ساخته شد! 🔥", reply_markup=back_to_main_kb(), parse_mode="HTML")


@router.callback_query(F.data == "habit:check")
async def habit_check(callback: CallbackQuery):
    habits = await q.get_habits(callback.from_user.id)
    if not habits:
        await callback.answer("عادتی نیست", show_alert=True)
        return
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for h in habits:
        builder.row(InlineKeyboardButton(
            text=f"{h.get('emoji', '🔥')} {h['name']}",
            callback_data=f"habit:done:{h['id']}"
        ))
    builder.row(InlineKeyboardButton(text="🔙", callback_data="menu:habits"))
    
    await callback.message.edit_text("کدام عادت رو امروز انجام دادی؟", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("habit:done:"))
async def habit_done(callback: CallbackQuery):
    habit_id = int(callback.data.split(":")[2])
    await q.log_habit(callback.from_user.id, habit_id)
    await callback.answer("✅ تیک زده شد! ادامه بده 🔥", show_alert=True)
    await habits_menu(callback)
