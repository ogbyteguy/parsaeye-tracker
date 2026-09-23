"""
ابزارهای تاریخ و ساعت جلالی
"""
import jdatetime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TEHRAN = ZoneInfo("Asia/Tehran")


def now_jalali() -> str:
    """تاریخ و ساعت فعلی جلالی به صورت رشته"""
    return jdatetime.datetime.now(TEHRAN).strftime("%Y/%m/%d %H:%M")


def today_jalali() -> str:
    """تاریخ امروز جلالی YYYY/MM/DD"""
    return jdatetime.date.today().strftime("%Y/%m/%d")


def yesterday_jalali() -> str:
    d = jdatetime.date.today() - jdatetime.timedelta(days=1)
    return d.strftime("%Y/%m/%d")


def tomorrow_jalali() -> str:
    d = jdatetime.date.today() + jdatetime.timedelta(days=1)
    return d.strftime("%Y/%m/%d")


def jalali_to_display(date_str: str) -> str:
    """تبدیل YYYY/MM/DD به نمایش زیباتر"""
    try:
        y, m, d = map(int, date_str.split("/"))
        months = ["", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                  "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
        return f"{d} {months[m]} {y}"
    except:
        return date_str


def get_week_range() -> tuple[str, str]:
    """شروع و پایان هفته جاری (شنبه تا جمعه)"""
    today = jdatetime.date.today()
    # شنبه = 6 در jdatetime (0=شنبه؟ بسته به نسخه)
    weekday = today.weekday()  # 0 = شنبه در jdatetime
    start = today - jdatetime.timedelta(days=weekday)
    end = start + jdatetime.timedelta(days=6)
    return start.strftime("%Y/%m/%d"), end.strftime("%Y/%m/%d")


def get_month_range() -> tuple[str, str]:
    today = jdatetime.date.today()
    start = today.replace(day=1)
    if today.month == 12:
        end = today.replace(year=today.year + 1, month=1, day=1) - jdatetime.timedelta(days=1)
    else:
        end = today.replace(month=today.month + 1, day=1) - jdatetime.timedelta(days=1)
    return start.strftime("%Y/%m/%d"), end.strftime("%Y/%m/%d")


def current_month_str() -> str:
    return jdatetime.date.today().strftime("%Y/%m")
