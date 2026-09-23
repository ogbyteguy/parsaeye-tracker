from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import queries as q
from bot.keyboards.activities import activities_menu_kb, activities_list_kb, duration_quick_kb
from bot.keyboards.main_menu import back_to_main_kb
from bot.states.forms import AddActivity, LogActivity, AdHocActivity
from bot.services.categorization import categorize, get_category_emoji
from bot.utils.jalali import today_jalali

router = Router()


@router.callback_query(F.data == "menu:activities")
async def activities_menu(callback: CallbackQuery):
    text = (
        "⚡ <b>مدیریت فعالیت‌ها</b>\n\n"
        "فعالیت جدید تعریف کن، زمان ثبت کن یا فعالیت خارج از برنامه اضافه کن.\n"
        "ربات خودش دسته‌بندی هوشمند انجام می‌ده."
    )
    await callback.message.edit_text(text, reply_markup=activities_menu_kb(), parse_mode="HTML")
    await callback.answer()


# ---------- افزودن فعالیت ----------
@router.callback_query(F.data == "act:add")
async def add_activity_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddActivity.name)
    await callback.message.edit_text(
        "📝 نام فعالیت رو بنویس (مثلاً: مطالعه زبان، باشگاه، کدنویسی):",
        reply_markup=back_to_main_kb()
    )
    await callback.answer()


@router.message(AddActivity.name)
async def add_activity_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddActivity.description)
    await message.answer("توضیحات کوتاه (اختیاری) رو بنویس یا /skip بزن:")


@router.message(AddActivity.description)
async def add_activity_desc(message: Message, state: FSMContext):
    desc = None if message.text == "/skip" else message.text.strip()
    data = await state.get_data()
    name = data["name"]
    
    category = categorize(name + " " + (desc or ""))
    emoji = get_category_emoji(category)
    
    act_id = await q.add_activity(
        user_id=message.from_user.id,
        name=name,
        description=desc,
        category=category,
        color_emoji=emoji
    )
    
    await state.clear()
    await message.answer(
        f"✅ فعالیت <b>{emoji} {name}</b> با موفقیت اضافه شد!\n"
        f"دسته: {category}",
        reply_markup=activities_menu_kb(),
        parse_mode="HTML"
    )


# ---------- لیست ----------
@router.callback_query(F.data == "act:list")
async def list_activities(callback: CallbackQuery):
    acts = await q.get_user_activities(callback.from_user.id)
    if not acts:
        await callback.message.edit_text(
            "هنوز فعالیتی تعریف نکردی.\nاول یکی اضافه کن.",
            reply_markup=activities_menu_kb()
        )
    else:
        text = "📋 <b>فعالیت‌های تو:</b>\n\n"
        for a in acts:
            text += f"{a.get('color_emoji', '⚡')} <b>{a['name']}</b> ({a.get('category', 'other')})\n"
        await callback.message.edit_text(text, reply_markup=activities_list_kb(acts, "act:info"), parse_mode="HTML")
    await callback.answer()


# ---------- ثبت زمان ----------
@router.callback_query(F.data == "act:log")
async def log_activity_start(callback: CallbackQuery, state: FSMContext):
    acts = await q.get_user_activities(callback.from_user.id)
    if not acts:
        await callback.answer("اول فعالیت تعریف کن!", show_alert=True)
        return
    await state.set_state(LogActivity.select)
    await callback.message.edit_text(
        "کدام فعالیت رو انجام دادی؟",
        reply_markup=activities_list_kb(acts, "act:select")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("act:select:"))
async def log_activity_selected(callback: CallbackQuery, state: FSMContext):
    act_id = int(callback.data.split(":")[2])
    await state.update_data(activity_id=act_id)
    await state.set_state(LogActivity.duration)
    await callback.message.edit_text(
        "چقدر زمان صرف کردی؟",
        reply_markup=duration_quick_kb(act_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("act:duration:"))
async def log_duration_quick(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    act_id = int(parts[2])
    minutes = int(parts[3])
    await state.update_data(duration=minutes, activity_id=act_id)
    await state.set_state(LogActivity.notes)
    await callback.message.edit_text("توضیحات یا نکته‌ای داری؟ (یا /skip)")
    await callback.answer()


@router.message(LogActivity.notes)
async def log_notes(message: Message, state: FSMContext):
    notes = None if message.text == "/skip" else message.text.strip()
    data = await state.get_data()
    
    await q.log_activity(
        user_id=message.from_user.id,
        activity_id=data["activity_id"],
        duration_minutes=data["duration"],
        notes=notes,
        is_planned=True
    )
    
    await state.clear()
    await message.answer(
        f"✅ ثبت شد! {data['duration']} دقیقه برای فعالیت.\nآفرین 💪",
        reply_markup=activities_menu_kb()
    )


# ---------- فعالیت خارج از برنامه ----------
@router.callback_query(F.data == "act:ad_hoc")
async def ad_hoc_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdHocActivity.name)
    await callback.message.edit_text(
        "نام فعالیت خارج از برنامه رو بنویس:",
        reply_markup=back_to_main_kb()
    )
    await callback.answer()


@router.message(AdHocActivity.name)
async def ad_hoc_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdHocActivity.duration)
    await message.answer("چقدر زمان؟ (عدد به دقیقه یا از دکمه‌ها)", reply_markup=duration_quick_kb())


@router.callback_query(F.data.startswith("act:duration_adhoc:"))
async def ad_hoc_duration(callback: CallbackQuery, state: FSMContext):
    minutes = int(callback.data.split(":")[2])
    data = await state.get_data()
    name = data.get("name", "فعالیت بدون نام")
    
    category = categorize(name)
    emoji = get_category_emoji(category)
    
    await q.log_activity(
        user_id=callback.from_user.id,
        activity_name=name,
        duration_minutes=minutes,
        is_planned=False
    )
    
    await state.clear()
    await callback.message.edit_text(
        f"✅ فعالیت خارج برنامه ثبت شد:\n{emoji} <b>{name}</b> — {minutes} دقیقه\nدسته: {category}",
        reply_markup=activities_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()
