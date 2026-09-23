"""
امتیازدهی هوشمند سیستم
"""
from bot.database import queries as q
from bot.utils.jalali import today_jalali


async def calculate_system_score(user_id: int, date: str = None) -> dict:
    """
    محاسبه امتیاز سیستم بر اساس:
    - تعداد فعالیت‌های ثبت‌شده
    - رعایت برنامه
    - پر کردن ژورنال
    - زمان مفید
    - ثبت مالی
    - عادت‌ها
    """
    date = date or today_jalali()
    score = 0.0
    max_score = 10.0
    strengths = []
    weaknesses = []

    # ۱. فعالیت‌ها (حداکثر ۳ امتیاز)
    logs = await q.get_activity_logs(user_id, date)
    total_acts = len(logs)
    total_minutes = sum(l.get("duration_minutes", 0) or 0 for l in logs)
    
    if total_acts >= 5:
        score += 3
        strengths.append("✅ تعداد فعالیت‌ها عالی بود")
    elif total_acts >= 3:
        score += 2
        strengths.append("✅ فعالیت‌های خوبی ثبت کردی")
    elif total_acts >= 1:
        score += 1
    else:
        weaknesses.append("❌ هیچ فعالیتی ثبت نشده")

    if total_minutes >= 180:  # ۳ ساعت
        score += 0.5
        strengths.append("⏱️ زمان مفید خوبی داشتی")

    # ۲. برنامه روزانه (حداکثر ۲ امتیاز)
    plan = await q.get_daily_plan(user_id, date)
    planned_done = sum(1 for l in logs if l.get("is_planned"))
    if plan:
        score += 1
        if planned_done >= 2:
            score += 1
            strengths.append("📅 برنامه را خوب رعایت کردی")
        else:
            weaknesses.append("📅 برنامه داشتی ولی کمتر اجرا شد")
    else:
        weaknesses.append("📅 برنامه روزانه تنظیم نشده بود")

    # ۳. ژورنال (حداکثر ۲ امتیاز)
    journal = await q.get_journal(user_id, date)
    if journal:
        filled_fields = sum(1 for k in ["good_things", "bad_things", "learned", "free_note"] 
                           if journal.get(k))
        if filled_fields >= 3:
            score += 2
            strengths.append("📝 ژورنال کامل نوشتی")
        elif filled_fields >= 1:
            score += 1
            strengths.append("📝 ژورنال نوشتی")
        else:
            score += 0.5
    else:
        weaknesses.append("📝 ژورنال امروز خالی است")

    # ۴. ترکر روزانه (حداکثر ۱ امتیاز)
    tracker = await q.get_daily_tracker(user_id, date)
    if tracker and (tracker.get("wake_time") or tracker.get("useful_work_minutes")):
        score += 1
        strengths.append("⏰ ترکر روزانه پر شده")
    else:
        weaknesses.append("⏰ ترکر روزانه ناقص است")

    # ۵. مالی (۰.۵ امتیاز)
    expenses = await q.get_expenses(user_id, date=date)
    if expenses:
        score += 0.5
        strengths.append("💰 خرج‌ها را ثبت کردی")

    # نرمال‌سازی به ۱۰
    final_score = min(round(score, 1), max_score)

    # ذخیره
    await q.save_daily_score(
        user_id=user_id,
        date=date,
        system_score=final_score,
        strengths=" | ".join(strengths) if strengths else None,
        weaknesses=" | ".join(weaknesses) if weaknesses else None,
        total_activities=total_acts,
        planned_done=planned_done,
        journal_filled=1 if journal else 0
    )

    return {
        "system_score": final_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "total_activities": total_acts,
        "total_minutes": total_minutes
    }
