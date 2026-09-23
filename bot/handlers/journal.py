from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb
from bot.states.forms import JournalForm
from bot.utils.jalali import today_jalali, jalali_to_display

router = Router()


@router.callback_query(F.data == "menu:journal")
async def journal_menu(callback: CallbackQuery):
    journal = await q.get_journal(callback.from_user.id)
    text = f"📝 <b>ژورنال روزانه</b>\n{jalali_to_display(today_jalali())}\n\n"
    
    if journal:
        text += "وضعیت امروز:\n"
        if journal.get("good_things"): text += f"😊 خوب‌ها: {journal['good_things'][:50]}...\n"
        if journal.get("bad_things"): text += f"😔 بدها: {journal['bad_things'][:50]}...\n"
        if journal.get("learned"): text += f"💡 یادگرفته: {journal['learned'][:50]}...\n"
        text += "\nمی‌تونی ویرایش کنی."
    else:
        text += "هنوز چیزی ننوشتی. شروع کنیم؟"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✍️ نوشتن/ویرایش ژورنال", callback_data="journal:write"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "journal:write")
async def journal_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JournalForm.good_things)
    await callback.message.edit_text(
        "😊 چیزهایی که حالت رو خوب کرد چی بود؟\n(یا /skip)"
    )
    await callback.answer()


@router.message(JournalForm.good_things)
async def journal_good(message: Message, state: FSMContext):
    val = None if message.text == "/skip" else message.text.strip()
    await state.update_data(good_things=val)
    await state.set_state(JournalForm.bad_things)
    await message.answer("😔 چیزهایی که حالت رو بد کرد؟\n(یا /skip)")


@router.message(JournalForm.bad_things)
async def journal_bad(message: Message, state: FSMContext):
    val = None if message.text == "/skip" else message.text.strip()
    await state.update_data(bad_things=val)
    await state.set_state(JournalForm.learned)
    await message.answer("💡 چیز خاصی که امروز یاد گرفتی؟\n(یا /skip)")


@router.message(JournalForm.learned)
async def journal_learned(message: Message, state: FSMContext):
    val = None if message.text == "/skip" else message.text.strip()
    await state.update_data(learned=val)
    await state.set_state(JournalForm.time_wasters)
    await message.answer("⏳ چیزهایی که خیلی زمان گرفت (مثبت یا منفی)؟\n(یا /skip)")


@router.message(JournalForm.time_wasters)
async def journal_time(message: Message, state: FSMContext):
    val = None if message.text == "/skip" else message.text.strip()
    await state.update_data(time_wasters=val)
    await state.set_state(JournalForm.free_note)
    await message.answer("📝 نوت آزاد یا هر چیزی که می‌خوای بنویسی:\n(یا /skip)")


@router.message(JournalForm.free_note)
async def journal_free(message: Message, state: FSMContext):
    val = None if message.text == "/skip" else message.text.strip()
    await state.update_data(free_note=val)
    await state.set_state(JournalForm.mood)
    await message.answer("از ۱ تا ۱۰ حالت کلی امروز چطور بود؟ (عدد بفرست)")


@router.message(JournalForm.mood)
async def journal_mood(message: Message, state: FSMContext):
    try:
        mood = int(message.text.strip())
        if not 1 <= mood <= 10:
            raise ValueError
    except:
        await message.answer("لطفاً عدد بین ۱ تا ۱۰ بفرست.")
        return
    
    data = await state.get_data()
    await q.save_journal(
        user_id=message.from_user.id,
        good_things=data.get("good_things"),
        bad_things=data.get("bad_things"),
        learned=data.get("learned"),
        time_wasters=data.get("time_wasters"),
        free_note=data.get("free_note"),
        mood_score=mood
    )
    await state.clear()
    
    await message.answer(
        f"✅ ژورنال امروز ذخیره شد!\nحالت: {mood}/10\nآفرین که نوشتی 🌱",
        reply_markup=back_to_main_kb()
    )
