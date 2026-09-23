from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb
from bot.states.forms import StudyLog
from bot.utils.jalali import today_jalali, jalali_to_display

router = Router()


@router.callback_query(F.data == "menu:study")
async def study_menu(callback: CallbackQuery):
    subjects = await q.get_subjects(callback.from_user.id)
    logs = await q.get_study_logs(callback.from_user.id)
    
    text = f"📚 <b>درس و مطالعه</b>\n{jalali_to_display(today_jalali())}\n\n"
    text += f"تعداد دروس تعریف‌شده: {len(subjects)}\n"
    text += f"ثبت‌های امروز: {len(logs)}\n"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ افزودن درس", callback_data="study:add_subject"))
    builder.row(InlineKeyboardButton(text="📖 ثبت مطالعه امروز", callback_data="study:log"))
    builder.row(InlineKeyboardButton(text="📋 دروس من", callback_data="study:list"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "study:add_subject")
async def add_subject_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StudyLog.subject)  # reuse for simplicity
    await callback.message.edit_text("نام درس رو بنویس:")
    await callback.answer()


@router.message(StudyLog.subject)
async def add_subject_name(message: Message, state: FSMContext):
    # برای افزودن درس ساده
    name = message.text.strip()
    await q.add_subject(message.from_user.id, name)
    await state.clear()
    await message.answer(f"✅ درس <b>{name}</b> اضافه شد.", reply_markup=back_to_main_kb(), parse_mode="HTML")


@router.callback_query(F.data == "study:log")
async def study_log_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StudyLog.book)
    await callback.message.edit_text("نام کتاب یا مبحثی که خوندی:")
    await callback.answer()


@router.message(StudyLog.book)
async def study_book(message: Message, state: FSMContext):
    await state.update_data(book_name=message.text.strip())
    await state.set_state(StudyLog.pages)
    await message.answer("چند صفحه خوندی؟ (عدد یا /skip)")


@router.message(StudyLog.pages)
async def study_pages(message: Message, state: FSMContext):
    pages = 0
    if message.text != "/skip":
        try:
            pages = int(message.text.strip())
        except:
            pass
    await state.update_data(pages_read=pages)
    await state.set_state(StudyLog.duration)
    await message.answer("چقدر زمان (دقیقه)؟")


@router.message(StudyLog.duration)
async def study_duration(message: Message, state: FSMContext):
    try:
        mins = int(message.text.strip())
    except:
        mins = 0
    data = await state.get_data()
    
    await q.add_study_log(
        user_id=message.from_user.id,
        book_name=data.get("book_name"),
        pages_read=data.get("pages_read", 0),
        duration_minutes=mins
    )
    await state.clear()
    await message.answer("✅ مطالعه ثبت شد! ادامه بده 📖", reply_markup=back_to_main_kb())
