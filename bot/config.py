from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: str = ""          # به صورت رشته می‌گیریم
    DATABASE_PATH: str = "data/bot.db"
    TIMEZONE: str = "Asia/Tehran"
    REMINDER_HOURS: str = "6,9,12,15,18,21"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

settings = Settings()
