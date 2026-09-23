"""
نقطه ورود اصلی ربات
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.database.db import init_db

# Handlers
from bot.handlers import start, profile, activities, daily_plan, journal, finance, study, habits, reports, admin

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, "INFO"))
logger = logging.getLogger(__name__)


async def main():
    # دیتابیس
    await init_db()
    
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # ثبت روترها
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(activities.router)
    dp.include_router(daily_plan.router)
    dp.include_router(journal.router)
    dp.include_router(finance.router)
    dp.include_router(study.router)
    dp.include_router(habits.router)
    dp.include_router(reports.router)
    dp.include_router(admin.router)
    
    logger.info("🚀 Bot is starting...")
    
    # حذف webhook و شروع polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
