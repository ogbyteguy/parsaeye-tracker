from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import queries as q
from bot.keyboards.main_menu import back_to_main_kb
from bot.states.forms import ExpenseForm, CommitmentForm
from bot.utils.jalali import today_jalali, jalali_to_display, current_month_str

router = Router()

TIPS = [
    "💡 هر خرج کوچک را هم ثبت کن تا تصویر واقعی داشته باشی.",
    "💡 قبل از خرید غیرضروری ۲۴ ساعت صبر کن.",
    "💡 بودجه ماهانه را واقع‌بینانه تعیین کن.",
    "💡 اقساط را در ابتدای ماه کنار بگذار."
]


@router.callback_query(F.data == "menu:finance")
async def finance_menu(callback: CallbackQuery):
    user = await q.get_user(callback.from_user.id)
    expenses = await q.get_expenses(callback.from_user.id, month=current_month_str())
    total = sum(e["amount"] for e in expenses)
    budget = user.get("monthly_budget") or 0
    
    import random
    tip = random.choice(TIPS)
    
    text = (
        f"💰 <b>مدیریت مالی</b>\n"
        f"ماه جاری: {current_month_str()}\n\n"
        f"📊 مجموع خرج این ماه: <b>{total:,.0f}</b> تومان\n"
        f"🎯 بودجه ماهانه: {budget:,.0f} تومان\n"
    )
    if budget > 0:
        percent = min(100, int(total / budget * 100))
        text += f"پیشرفت بودجه: {percent}%\n"
    
    text += f"\n{tip}"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ ثبت خرج", callback_data="fin:expense"))
    builder.row(InlineKeyboardButton(text="📋 لیست خرج‌های امروز", callback_data="fin:list_today"))
    builder.row(InlineKeyboardButton(text="📅 اقساط و قول‌ها", callback_data="fin:commitments"))
    builder.row(InlineKeyboardButton(text="🎯 تنظیم بودجه ماهانه", callback_data="fin:budget"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "fin:expense")
async def expense_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseForm.amount)
    await callback.message.edit_text("مبلغ خرج رو به تومان بنویس (فقط عدد):")
    await callback.answer()


@router.message(ExpenseForm.amount)
async def expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "").strip())
    except:
        await message.answer("لطفاً عدد معتبر وارد کن.")
        return
    await state.update_data(amount=amount)
    await state.set_state(ExpenseForm.category)
    await message.answer("دسته‌بندی؟ (مثلاً غذا، حمل‌ونقل، تفریح) یا /skip")


@router.message(ExpenseForm.category)
async def expense_cat(message: Message, state: FSMContext):
    cat = None if message.text == "/skip" else message.text.strip()
    await state.update_data(category=cat)
    await state.set_state(ExpenseForm.description)
    await message.answer("توضیح کوتاه (اختیاری) یا /skip")


@router.message(ExpenseForm.description)
async def expense_desc(message: Message, state: FSMContext):
    desc = None if message.text == "/skip" else message.text.strip()
    await state.update_data(description=desc)
    await state.set_state(ExpenseForm.feeling)
    await message.answer("احساست نسبت به این خرج؟ (مثلاً لازم بود، پشیمونم، خوبه) یا /skip")


@router.message(ExpenseForm.feeling)
async def expense_feeling(message: Message, state: FSMContext):
    feeling = None if message.text == "/skip" else message.text.strip()
    data = await state.get_data()
    
    await q.add_expense(
        user_id=message.from_user.id,
        amount=data["amount"],
        category=data.get("category"),
        description=data.get("description"),
        feeling=feeling
    )
    await state.clear()
    
    await message.answer(
        f"✅ خرج {data['amount']:,.0f} تومان ثبت شد.",
        reply_markup=back_to_main_kb()
    )


@router.callback_query(F.data == "fin:list_today")
async def list_today_expenses(callback: CallbackQuery):
    expenses = await q.get_expenses(callback.from_user.id, date=today_jalali())
    if not expenses:
        text = "امروز خرجی ثبت نشده."
    else:
        text = f"📋 خرج‌های امروز ({jalali_to_display(today_jalali())}):\n\n"
        total = 0
        for e in expenses:
            text += f"• {e['amount']:,.0f} — {e.get('category') or 'عمومی'} {e.get('feeling') or ''}\n"
            total += e["amount"]
        text += f"\nجمع: <b>{total:,.0f}</b> تومان"
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "fin:commitments")
async def commitments_menu(callback: CallbackQuery):
    commits = await q.get_commitments(callback.from_user.id)
    text = "📅 <b>اقساط، قرض‌ها و قول‌ها</b>\n\n"
    if commits:
        for c in commits:
            text += f"• {c['title']} — {c.get('amount') or '—'} — موعد: {c.get('due_date') or '—'}\n"
    else:
        text += "موردی ثبت نشده."
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ افزودن", callback_data="fin:add_commit"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:finance"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()
