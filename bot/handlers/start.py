from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from bot.database import queries as q
from bot.keyboards.main_menu import main_menu_kb, back_to_main_kb
from bot.config import settings
from bot.utils.jalali import today_jalali, jalali_to_display

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await q.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    
    is_admin = bool(user.get("is_admin")) or (message.from_user.id in getattr(settings, "ADMIN_IDS", []))
    
    text = (
        f"سلام {message.from_user.first_name} عزیز! 🌟\n\n"
        f"به ربات مدیریت زندگی و بهره‌وری خوش اومدی.\n"
        f"امروز: <b>{jalali_to_display(today_jalali())}</b>\n\n"
        "با این ربات می‌تونی:\n"
        "• فعالیت‌ها و زمانت رو ردیابی کنی\n"
        "• برنامه روزانه بنویسی و مقایسه کنی\n"
        "• ژورنال بنویسی و احساس‌هات رو ثبت کنی\n"
        "• خرج‌ها و اقساط رو مدیریت کنی\n"
        "• مطالعه و درسات رو پیگیری کنی\n"
        "• عادت بسازی و امتیاز بگیری\n\n"
        "از منوی زیر شروع کن 👇"
    )
    
    await message.answer(text, reply_markup=main_menu_kb(is_admin=is_admin), parse_mode="HTML")


@router.message(F.text == settings.ADMIN_SECRET)
async def become_admin(message: Message):
    """با فرستادن رمز مخفی، کاربر ادمین می‌شود"""
    await q.update_user(message.from_user.id, is_admin=1)
    
    await message.answer(
        "✅ شما با موفقیت به عنوان <b>ادمین</b> ثبت شدید!\n"
        "حالا از منوی اصلی می‌تونی به پنل ادمین دسترسی داشته باشی.",
        parse_mode="HTML"
    )
    
    await message.answer(
        "منوی اصلی به‌روز شد:",
        reply_markup=main_menu_kb(is_admin=True)
    )


@router.callback_query(F.data == "menu:main")
async def back_to_main(callback: CallbackQuery):
    user = await q.get_user(callback.from_user.id)
    is_admin = bool(user and user.get("is_admin")) or (callback.from_user.id in getattr(settings, "ADMIN_IDS", []))
    
    await callback.message.edit_text(
        "🏠 <b>منوی اصلی</b>\n\nیکی از بخش‌ها رو انتخاب کن:",
        reply_markup=main_menu_kb(is_admin=is_admin),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:help")
async def help_menu(callback: CallbackQuery):
    text = (
        "📖 <b>راهنمای ربات</b>\n\n"
        "🔹 <b>فعالیت‌ها</b>: فعالیت تعریف کن و زمان سپری‌شده رو ثبت کن.\n"
        "🔹 <b>برنامه روزانه</b>: از شب قبل برنامه بنویس، ربات مقایسه‌ش می‌کنه.\n"
        "🔹 <b>ژورنال</b>: هر روز چند سؤال ساده برای خودآگاهی.\n"
        "🔹 <b>مالی</b>: خرج‌ها + احساس + اقساط و یادآوری.\n"
        "🔹 <b>درس</b>: پیشرفت مطالعه و تست‌ها.\n"
        "🔹 <b>عادت‌ها</b>: عادت بساز و استریک بگیر.\n"
        "🔹 <b>گزارش‌ها</b>: روزانه/هفتگی/ماهانه با امتیاز.\n\n"
        "💡 همه تاریخ‌ها جلالی هستن.\n"
        "دکمه‌های شیشه‌ای رو لمس کن و لذت ببر!"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "menu:settings")
async def settings_menu(callback: CallbackQuery):
    text = (
        "⚙️ <b>تنظیمات</b>\n\n"
        "این بخش به زودی کامل‌تر می‌شود.\n\n"
        "فعلاً می‌تونی:\n"
        "• برای ادمین شدن رمز مخفی رو ارسال کنی\n"
        "• از منوی اصلی استفاده کنی"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="HTML")
    await callback.answer()
