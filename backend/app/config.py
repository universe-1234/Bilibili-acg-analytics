import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Bilibili ACG Analytics"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production-2024-bilibili-acg"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DB_TYPE: str = "sqlite"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root123456"
    DB_NAME: str = "bilibili_acg"

    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "sqlite":
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_dir = os.path.join(base, "data")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "bilibili_acg.db")
            return f"sqlite:///{db_path}"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
