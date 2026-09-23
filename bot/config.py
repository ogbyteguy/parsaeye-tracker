from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int] = []
    DATABASE_PATH: str = "data/bot.db"
    TIMEZONE: str = "Asia/Tehran"
    REMINDER_HOURS: List[int] = [6, 9, 12, 15, 18, 21]
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse ADMIN_IDS from comma-separated string if needed
        if isinstance(self.ADMIN_IDS, str):
            self.ADMIN_IDS = [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

settings = Settings()
