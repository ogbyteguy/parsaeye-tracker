"""
مدل‌های دیتابیس - SQLite
"""

SCHEMA = """
-- کاربران
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    join_date TEXT NOT NULL,          -- جلالی
    is_admin INTEGER DEFAULT 0,
    timezone TEXT DEFAULT 'Asia/Tehran',
    wake_time TEXT,                   -- ساعت بیداری پیش‌فرض
    sleep_time TEXT,
    monthly_budget REAL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    last_active TEXT
);

-- فعالیت‌ها (تعریف شده توسط کاربر)
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,                    -- sport, study, work, health, selfdev, other
    is_side INTEGER DEFAULT 0,        -- فعالیت جانبی
    color_emoji TEXT DEFAULT '⚡',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ثبت زمان فعالیت‌ها (لاگ روزانه)
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER,
    activity_name TEXT,               -- برای فعالیت‌های ad-hoc
    date TEXT NOT NULL,               -- جلالی YYYY/MM/DD
    duration_minutes INTEGER DEFAULT 0,
    notes TEXT,
    is_planned INTEGER DEFAULT 1,     -- آیا در برنامه بود؟
    feeling INTEGER,                  -- ۱ تا ۱۰
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);

-- برنامه روزانه
CREATE TABLE IF NOT EXISTS daily_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_date TEXT NOT NULL,          -- جلالی
    content TEXT NOT NULL,            -- JSON لیست فعالیت‌ها + زمان تخمینی
    is_completed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, plan_date),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ترکر روزانه (بیداری، خواب، گوشی و ...)
CREATE TABLE IF NOT EXISTS daily_trackers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    wake_time TEXT,
    sleep_time TEXT,
    phone_usage_estimate INTEGER,     -- دقیقه
    useful_work_minutes INTEGER,
    notes TEXT,
    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ژورنال و احساس‌نویسی
CREATE TABLE IF NOT EXISTS journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    good_things TEXT,
    bad_things TEXT,
    learned TEXT,
    time_wasters TEXT,
    free_note TEXT,
    mood_score INTEGER,               -- ۱ تا ۱۰
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- امتیاز روزانه
CREATE TABLE IF NOT EXISTS daily_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    user_score REAL,                  -- امتیاز خود کاربر
    system_score REAL,                -- امتیاز سیستم
    strengths TEXT,
    weaknesses TEXT,
    total_activities INTEGER DEFAULT 0,
    planned_done INTEGER DEFAULT 0,
    journal_filled INTEGER DEFAULT 0,
    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- مالی: خرج‌ها
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT,
    description TEXT,
    feeling TEXT,                     -- احساس نسبت به خرج
    date TEXT NOT NULL,               -- جلالی
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- اقساط، قرض‌ها، قول‌ها
CREATE TABLE IF NOT EXISTS financial_commitments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    amount REAL,
    due_date TEXT,                    -- جلالی
    type TEXT,                        -- installment, debt, promise
    is_paid INTEGER DEFAULT 0,
    notes TEXT,
    reminder_sent INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- دروس و مطالعه
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    short_goal TEXT,
    long_goal TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS study_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_id INTEGER,
    book_name TEXT,
    genre TEXT,
    pages_read INTEGER DEFAULT 0,
    tests_done INTEGER DEFAULT 0,
    method TEXT,
    topics TEXT,
    duration_minutes INTEGER DEFAULT 0,
    summary TEXT,
    date TEXT NOT NULL,
    is_finished_book INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- عادت‌ها (Habit Tracker)
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    emoji TEXT DEFAULT '🔥',
    target_per_week INTEGER DEFAULT 7,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    done INTEGER DEFAULT 1,
    UNIQUE(user_id, habit_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (habit_id) REFERENCES habits(id)
);

-- تنظیمات کاربر
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,
    reminders_enabled INTEGER DEFAULT 1,
    reminder_hours TEXT DEFAULT '6,9,12,15,18,21',
    language TEXT DEFAULT 'fa',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ایندکس‌ها برای سرعت
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_date ON activity_logs(user_id, date);
CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, date);
CREATE INDEX IF NOT EXISTS idx_journals_user_date ON journals(user_id, date);
CREATE INDEX IF NOT EXISTS idx_daily_scores_user_date ON daily_scores(user_id, date);
"""
