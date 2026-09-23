"""
دسته‌بندی هوشمند فعالیت‌ها بر اساس دیکشنری کلمات کلیدی
"""
import json
from pathlib import Path

DICT_PATH = Path(__file__).parent.parent.parent / "data" / "dictionaries.json"

DEFAULT_DICT = {
    "sport": ["ورزش", "دویدن", "پیاده‌روی", "باشگاه", "شنا", "یوگا", "فوتبال", "بدنسازی", "ورزشی", "تمرین"],
    "study": ["مطالعه", "درس", "کتاب", "خواندن", "تست", "کنکور", "یادگیری", "آموزش", "مقاله", "جزوه"],
    "work": ["کار", "پروژه", "جلسه", "ایمیل", "کدنویسی", "برنامه", "وظیفه", "اداره", "فریلنس"],
    "health": ["خواب", "غذا", "آب", "مدیتیشن", "آرامش", "بهداشت", "مسواک", "دوش", "سلامت", "ویتامین"],
    "selfdev": ["خودتوسعه", "عادت", "برنامه", "هدف", "انگیزه", "ژورنال", "فکر", "رشد", "مهارت", "زبان"],
    "finance": ["خرج", "پول", "بودجه", "قسط", "پس‌انداز", "سرمایه‌گذاری", "بانک"],
    "social": ["دوست", "خانواده", "گفتگو", "مهمانی", "تماس", "پیام"],
    "entertainment": ["فیلم", "سریال", "موسیقی", "بازی", "اینستاگرام", "یوتیوب", "تفریح"]
}


def load_dictionary() -> dict:
    if DICT_PATH.exists():
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # ایجاد فایل پیش‌فرض
    DICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DICT_PATH, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_DICT, f, ensure_ascii=False, indent=2)
    return DEFAULT_DICT


def categorize(text: str) -> str:
    """دسته‌بندی متن بر اساس کلمات کلیدی"""
    text = text.lower()
    dictionary = load_dictionary()
    
    scores = {}
    for category, keywords in dictionary.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return "other"
    
    return max(scores, key=scores.get)


def get_category_emoji(category: str) -> str:
    emojis = {
        "sport": "🏃",
        "study": "📚",
        "work": "💼",
        "health": "🌿",
        "selfdev": "🚀",
        "finance": "💰",
        "social": "👥",
        "entertainment": "🎮",
        "other": "⚡"
    }
    return emojis.get(category, "⚡")
