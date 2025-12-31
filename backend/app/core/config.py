from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/restaurant_db"

    # 静态文件路径
    STATIC_FILES_PATH: str = "/Volumes/545S/general final/Material/material"
    STATIC_URL_PREFIX: str = "/static"

    # Material数据路径
    MATERIAL_PATH: str = "/Volumes/545S/general final/Material/material"

    # 应用配置
    APP_NAME: str = "Restaurant Management System"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379/0"

    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    HOT_PRODUCTS_CACHE_TTL: int = 1800  # 30分钟
    PRODUCT_LIST_CACHE_TTL: int = 600  # 10分钟

    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    """获取配置单例"""
    return Settings()
