import aiosqlite
import os
from pathlib import Path
from bot.config import settings
from bot.database.models import SCHEMA

DB_PATH = settings.DATABASE_PATH

async def init_db():
    """ایجاد دیتابیس و جداول"""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()
    print(f"✅ Database initialized at {DB_PATH}")

async def get_db():
    """دریافت اتصال دیتابیس"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db
