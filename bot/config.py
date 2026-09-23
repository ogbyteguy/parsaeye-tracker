from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: Union[str, int, List[int]] = ""
    DATABASE_PATH: str = "data/bot.db"
    TIMEZONE: str = "Asia/Tehran"
    REMINDER_HOURS: str = "6,9,12,15,18,21"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, int):
            return [v]
        if isinstance(v, list):
            return v
        # رشته مثل "123,456"
        return [int(x.strip()) for x in str(v).split(",") if x.strip()]

settings = Settings()
