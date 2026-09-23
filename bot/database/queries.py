"""
تمام کوئری‌های دیتابیس
"""
import aiosqlite
from typing import Optional, List, Dict, Any
from bot.database.db import get_db
from bot.utils.jalali import today_jalali, now_jalali


# ==================== USERS ====================
async def get_or_create_user(user_id: int, username: str = None, full_name: str = None) -> dict:
    db = await get_db()
    try:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                await db.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now_jalali(), user_id))
                await db.commit()
                return dict(row)
        
        # کاربر جدید
        await db.execute(
            """INSERT INTO users (user_id, username, full_name, join_date, last_active)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, username, full_name, today_jalali(), now_jalali())
        )
        await db.execute("INSERT INTO user_settings (user_id) VALUES (?)", (user_id,))
        await db.commit()
        
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return dict(await cursor.fetchone())
    finally:
        await db.close()


async def get_user(user_id: int) -> Optional[dict]:
    db = await get_db()
    try:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await db.close()


async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    db = await get_db()
    try:
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [user_id]
        await db.execute(f"UPDATE users SET {sets} WHERE user_id = ?", values)
        await db.commit()
    finally:
        await db.close()


async def get_all_users() -> List[dict]:
    db = await get_db()
    try:
        async with db.execute("SELECT * FROM users ORDER BY join_date DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        await db.close()


async def count_users() -> int:
    db = await get_db()
    try:
        async with db.execute("SELECT COUNT(*) as cnt FROM users") as cursor:
            row = await cursor.fetchone()
            return row["cnt"]
    finally:
        await db.close()


# ==================== ACTIVITIES ====================
async def add_activity(user_id: int, name: str, description: str = None, category: str = "other",
                       is_side: bool = False, color_emoji: str = "⚡") -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO activities (user_id, name, description, category, is_side, color_emoji)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, name, description, category, int(is_side), color_emoji)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_user_activities(user_id: int, include_side: bool = True) -> List[dict]:
    db = await get_db()
    try:
        query = "SELECT * FROM activities WHERE user_id = ?"
        if not include_side:
            query += " AND is_side = 0"
        query += " ORDER BY name"
        async with db.execute(query, (user_id,)) as cursor:
            return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


async def log_activity(user_id: int, activity_id: int = None, activity_name: str = None,
                       duration_minutes: int = 0, notes: str = None, is_planned: bool = True,
                       feeling: int = None, date: str = None) -> int:
    date = date or today_jalali()
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO activity_logs 
               (user_id, activity_id, activity_name, date, duration_minutes, notes, is_planned, feeling)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, activity_id, activity_name, date, duration_minutes, notes, int(is_planned), feeling)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_activity_logs(user_id: int, date: str = None) -> List[dict]:
    date = date or today_jalali()
    db = await get_db()
    try:
        async with db.execute(
            """SELECT al.*, a.name as act_name, a.color_emoji 
               FROM activity_logs al
               LEFT JOIN activities a ON al.activity_id = a.id
               WHERE al.user_id = ? AND al.date = ?
               ORDER BY al.created_at""",
            (user_id, date)
        ) as cursor:
            return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


async def delete_activity(user_id: int, activity_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM activities WHERE id = ? AND user_id = ?", (activity_id, user_id))
        await db.commit()
    finally:
        await db.close()


# ==================== DAILY PLAN ====================
async def save_daily_plan(user_id: int, plan_date: str, content: str):
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO daily_plans (user_id, plan_date, content)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, plan_date) DO UPDATE SET content = excluded.content""",
            (user_id, plan_date, content)
        )
        await db.commit()
    finally:
        await db.close()


async def get_daily_plan(user_id: int, plan_date: str = None) -> Optional[dict]:
    plan_date = plan_date or today_jalali()
    db = await get_db()
    try:
        async with db.execute(
            "SELECT * FROM daily_plans WHERE user_id = ? AND plan_date = ?",
            (user_id, plan_date)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await db.close()


# ==================== DAILY TRACKER ====================
async def save_daily_tracker(user_id: int, date: str = None, **kwargs):
    date = date or today_jalali()
    db = await get_db()
    try:
        # بررسی وجود
        async with db.execute(
            "SELECT id FROM daily_trackers WHERE user_id = ? AND date = ?", (user_id, date)
        ) as cursor:
            exists = await cursor.fetchone()
        
        if exists:
            sets = ", ".join(f"{k} = ?" for k in kwargs)
            values = list(kwargs.values()) + [user_id, date]
            await db.execute(f"UPDATE daily_trackers SET {sets} WHERE user_id = ? AND date = ?", values)
        else:
            cols = ", ".join(["user_id", "date"] + list(kwargs.keys()))
            placeholders = ", ".join(["?"] * (2 + len(kwargs)))
            values = [user_id, date] + list(kwargs.values())
            await db.execute(f"INSERT INTO daily_trackers ({cols}) VALUES ({placeholders})", values)
        await db.commit()
    finally:
        await db.close()


async def get_daily_tracker(user_id: int, date: str = None) -> Optional[dict]:
    date = date or today_jalali()
    db = await get_db()
    try:
        async with db.execute(
            "SELECT * FROM daily_trackers WHERE user_id = ? AND date = ?", (user_id, date)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await db.close()


# ==================== JOURNAL ====================
async def save_journal(user_id: int, date: str = None, **kwargs):
    date = date or today_jalali()
    db = await get_db()
    try:
        async with db.execute(
            "SELECT id FROM journals WHERE user_id = ? AND date = ?", (user_id, date)
        ) as cursor:
            exists = await cursor.fetchone()
        
        if exists:
            sets = ", ".join(f"{k} = ?" for k in kwargs)
            values = list(kwargs.values()) + [user_id, date]
            await db.execute(f"UPDATE journals SET {sets} WHERE user_id = ? AND date = ?", values)
        else:
            cols = ", ".join(["user_id", "date"] + list(kwargs.keys()))
            placeholders = ", ".join(["?"] * (2 + len(kwargs)))
            values = [user_id, date] + list(kwargs.values())
            await db.execute(f"INSERT INTO journals ({cols}) VALUES ({placeholders})", values)
        await db.commit()
    finally:
        await db.close()


async def get_journal(user_id: int, date: str = None) -> Optional[dict]:
    date = date or today_jalali()
    db = await get_db()
    try:
        async with db.execute(
            "SELECT * FROM journals WHERE user_id = ? AND date = ?", (user_id, date)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await db.close()


# ==================== SCORES ====================
async def save_daily_score(user_id: int, date: str, user_score: float = None, system_score: float = None,
                           strengths: str = None, weaknesses: str = None, **kwargs):
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO daily_scores 
               (user_id, date, user_score, system_score, strengths, weaknesses, total_activities, planned_done, journal_filled)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id, date) DO UPDATE SET
                   user_score = COALESCE(excluded.user_score, user_score),
                   system_score = COALESCE(excluded.system_score, system_score),
                   strengths = COALESCE(excluded.strengths, strengths),
                   weaknesses = COALESCE(excluded.weaknesses, weaknesses),
                   total_activities = COALESCE(excluded.total_activities, total_activities),
                   planned_done = COALESCE(excluded.planned_done, planned_done),
                   journal_filled = COALESCE(excluded.journal_filled, journal_filled)
            """,
            (user_id, date, user_score, system_score, strengths, weaknesses,
             kwargs.get("total_activities", 0), kwargs.get("planned_done", 0), kwargs.get("journal_filled", 0))
        )
        await db.commit()
    finally:
        await db.close()


async def get_daily_score(user_id: int, date: str = None) -> Optional[dict]:
    date = date or today_jalali()
    db = await get_db()
    try:
        async with db.execute(
            "SELECT * FROM daily_scores WHERE user_id = ? AND date = ?", (user_id, date)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await db.close()


async def get_scores_range(user_id: int, start_date: str, end_date: str) -> List[dict]:
    db = await get_db()
    try:
        async with db.execute(
            """SELECT * FROM daily_scores 
               WHERE user_id = ? AND date BETWEEN ? AND ?
               ORDER BY date""",
            (user_id, start_date, end_date)
        ) as cursor:
            return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


# ==================== FINANCE ====================
async def add_expense(user_id: int, amount: float, category: str = None, description: str = None,
                      feeling: str = None, date: str = None) -> int:
    date = date or today_jalali()
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO expenses (user_id, amount, category, description, feeling, date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, amount, category, description, feeling, date)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_expenses(user_id: int, date: str = None, month: str = None) -> List[dict]:
    db = await get_db()
    try:
        if date:
            async with db.execute(
                "SELECT * FROM expenses WHERE user_id = ? AND date = ? ORDER BY created_at DESC",
                (user_id, date)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]
        elif month:  # ماه به صورت YYYY/MM
            async with db.execute(
                "SELECT * FROM expenses WHERE user_id = ? AND date LIKE ? ORDER BY date DESC",
                (user_id, f"{month}%")
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]
        else:
            async with db.execute(
                "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT 50",
                (user_id,)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


async def add_commitment(user_id: int, title: str, amount: float = None, due_date: str = None,
                         type_: str = "promise", notes: str = None) -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO financial_commitments (user_id, title, amount, due_date, type, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title, amount, due_date, type_, notes)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_commitments(user_id: int, only_unpaid: bool = True) -> List[dict]:
    db = await get_db()
    try:
        query = "SELECT * FROM financial_commitments WHERE user_id = ?"
        if only_unpaid:
            query += " AND is_paid = 0"
        query += " ORDER BY due_date"
        async with db.execute(query, (user_id,)) as cursor:
            return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


# ==================== STUDY ====================
async def add_subject(user_id: int, name: str, short_goal: str = None, long_goal: str = None) -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO subjects (user_id, name, short_goal, long_goal) VALUES (?, ?, ?, ?)",
            (user_id, name, short_goal, long_goal)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_subjects(user_id: int) -> List[dict]:
    db = await get_db()
    try:
        async with db.execute("SELECT * FROM subjects WHERE user_id = ? ORDER BY name", (user_id,)) as cursor:
            return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


async def add_study_log(user_id: int, date: str = None, **kwargs) -> int:
    date = date or today_jalali()
    db = await get_db()
    try:
        cols = ["user_id", "date"] + list(kwargs.keys())
        placeholders = ", ".join(["?"] * len(cols))
        values = [user_id, date] + list(kwargs.values())
        cursor = await db.execute(
            f"INSERT INTO study_logs ({', '.join(cols)}) VALUES ({placeholders})", values
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_study_logs(user_id: int, date: str = None) -> List[dict]:
    date = date or today_jalali()
    db = await get_db()
    try:
        async with db.execute(
            """SELECT sl.*, s.name as subject_name 
               FROM study_logs sl
               LEFT JOIN subjects s ON sl.subject_id = s.id
               WHERE sl.user_id = ? AND sl.date = ?
               ORDER BY sl.created_at""",
            (user_id, date)
        ) as cursor:
            return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


# ==================== HABITS ====================
async def add_habit(user_id: int, name: str, emoji: str = "🔥", target_per_week: int = 7) -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO habits (user_id, name, emoji, target_per_week) VALUES (?, ?, ?, ?)",
            (user_id, name, emoji, target_per_week)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_habits(user_id: int) -> List[dict]:
    db = await get_db()
    try:
        async with db.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,)) as cursor:
            return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


async def log_habit(user_id: int, habit_id: int, date: str = None, done: bool = True):
    date = date or today_jalali()
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO habit_logs (user_id, habit_id, date, done)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, habit_id, date) DO UPDATE SET done = excluded.done""",
            (user_id, habit_id, date, int(done))
        )
        await db.commit()
    finally:
        await db.close()


async def get_habit_streak(user_id: int, habit_id: int) -> int:
    """محاسبه استریک فعلی"""
    db = await get_db()
    try:
        async with db.execute(
            """SELECT date FROM habit_logs 
               WHERE user_id = ? AND habit_id = ? AND done = 1
               ORDER BY date DESC""",
            (user_id, habit_id)
        ) as cursor:
            dates = [r["date"] for r in await cursor.fetchall()]
        
        if not dates:
            return 0
        
        # محاسبه ساده استریک (نیاز به منطق جلالی دقیق‌تر دارد)
        streak = 1
        # برای سادگی فعلاً تعداد روزهای متوالی از آخر را برمی‌گردانیم
        return min(len(dates), 30)  # محدودیت موقت
    finally:
        await db.close()
