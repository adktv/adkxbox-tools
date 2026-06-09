"""应用配置 - pydantic-settings 自动从 .env 读取。"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 环境
    env: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = True

    # API
    api_title: str = "adkxbox-tools API"
    api_version: str = "0.1.0"
    api_prefix: str = "/api"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # 数据库
    database_url: str = "sqlite:///./adkxbox.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # 鉴权
    jwt_secret: str = "CHANGE-ME-IN-PRODUCTION-please-use-openssl-rand-base64-32"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 限流
    rate_limit_per_minute: int = 60
    rate_limit_storage: str = "memory"  # "memory" | "redis"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """获取缓存的 settings 实例。"""
    return Settings()


settings = get_settings()
