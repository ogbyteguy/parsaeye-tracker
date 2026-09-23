# 🤖 ربات مدیریت زندگی و بهره‌وری (Telegram Productivity Bot)

ربات کامل و حرفه‌ای برای مدیریت شخصی، فعالیت‌ها، زمان، مالی، ژورنال، مطالعه و عادت‌سازی با رابط کاربری مدرن و تاریخ جلالی.

## ✨ ویژگی‌ها

- سیستم عضویت و پنل کاربری
- تعریف و ردیابی فعالیت‌ها + دسته‌بندی هوشمند
- برنامه‌ریزی روزانه و مقایسه با واقعیت
- ژورنال و احساس‌نویسی روزانه
- امتیازدهی هوشمند (کاربر + سیستم)
- مدیریت مالی (خرج + اقساط + بودجه)
- بخش درس و مطالعه
- عادت‌ساز با تیک روزانه
- گزارش روزانه / هفتگی / ماهانه
- پنل ادمین (آمار + پیام گروهی)
- تمام تاریخ‌ها جلالی
- دکمه‌های شیشه‌ای (Inline Keyboard)
- آماده دیپلوی روی Railway / Render / Fly.io

## 🚀 راه‌اندازی سریع

### ۱. ساخت ربات در تلگرام
1. به [@BotFather](https://t.me/BotFather) برو
2. `/newbot` بزن و توکن بگیر

### ۲. کلون و تنظیم
```bash
git clone <your-repo>
cd telegram_productivity_bot
cp .env.example .env
```

فایل `.env` را ویرایش کن:
```
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=your_telegram_id
```

### ۳. نصب و اجرا محلی
```bash
python -m venv venv
source venv/bin/activate  # ویندوز: venv\Scripts\activate
pip install -r requirements.txt
python -m bot.main
```

### ۴. دیپلوی روی Railway (پیشنهادی)
1. پروژه را روی GitHub بگذار
2. در [Railway.app](https://railway.app) New Project → Deploy from GitHub
3. متغیرهای محیطی را اضافه کن (BOT_TOKEN و ADMIN_IDS)
4. Deploy!

یا با Docker:
```bash
docker build -t productivity-bot .
docker run --env-file .env productivity-bot
```

## 📁 ساختار پروژه

```
bot/
├── main.py              # نقطه ورود
├── config.py
├── database/            # مدل‌ها و کوئری‌ها
├── handlers/            # تمام هندلرها
├── keyboards/           # کیبوردهای اینلاین
├── services/            # امتیازدهی و دسته‌بندی
├── states/              # FSM
└── utils/               # جلالی و ...
data/
└── dictionaries.json    # کلمات کلیدی دسته‌بندی
```

## 🔧 توسعه بیشتر

- برای اضافه کردن یادآوری خودکار می‌توان از APScheduler استفاده کرد (در requirements هست).
- دیکشنری کلمات در `data/dictionaries.json` قابل ویرایش است.
- برای ۲۰+ کاربر همزمان SQLite کافی است. در صورت نیاز به PostgreSQL مهاجرت کنید.

## 📝 نکات

- همه متن‌ها فارسی و کاربرپسند هستند.
- کد ماژولار و با کامنت است.
- مدیریت خطا پایه وجود دارد؛ برای production لاگ‌گیری پیشرفته‌تر اضافه کنید.

ساخته‌شده با ❤️ برای رشد شخصی.
