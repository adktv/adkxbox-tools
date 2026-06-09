"""核心模块 - 安全：JWT、密码（passlib + bcrypt 4.x 兼容性问题，改用 bcrypt 直接）。"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    """哈希密码。"""
    # bcrypt 限制 72 字节，截断防 overflow
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt(rounds=12)).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码。"""
    try:
        pwd_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed.encode("ascii"))
    except Exception:
        return False


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """生成 access token。"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str | int) -> str:
    """生成 refresh token。"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    """解码 token，失败返回 None。"""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


def generate_api_key() -> str:
    """生成 API key（用户用于第三方调用）。"""
    return f"adkx_{secrets.token_urlsafe(32)}"
