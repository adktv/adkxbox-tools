"""鉴权路由 - 注册 / 登录 / 刷新 / 当前用户。

注：@limiter.limit 在 body 参数路由上会触发 500（slowapi 0.1.x + FastAPI 0.115 +
OAuth2PasswordRequestForm/form 解析的兼容 bug）。Auth 限流改在 Caddy 层用 rate_limit
中间件代替（见 /etc/caddy/Caddyfile 的 tools.adkxbox.dpdns.org block）。
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlmodel import Session

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database import get_session
from app.models import User, UserCreate, UserPublic

logger = logging.getLogger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    session: Session = Depends(get_session),
) -> User:
    """注册新用户。"""
    # 用 raw SQL 检查存在性，避免 SQLModel 字段访问的 Pydantic v2 兼容 bug
    existing_row = session.execute(
        text("SELECT id FROM users WHERE username = :u OR email = :e LIMIT 1"),
        {"u": user_in.username, "e": user_in.email},
    ).first()
    if existing_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已被注册",
        )

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", summary="登录（OAuth2 form-data）")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> dict:
    """登录获取 access + refresh token。"""
    row = session.execute(
        text("SELECT id, hashed_password, is_active FROM users WHERE username = :u"),
        {"u": form_data.username},
    ).first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    user_id, hashed, is_active = row[0], row[1], row[2]
    if not hashed or not verify_password(form_data.password, hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用")

    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.post("/refresh", summary="刷新 access token")
async def refresh_token(refresh_token: str) -> dict:
    """用 refresh token 换新的 access token。"""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {
        "access_token": create_access_token(int(user_id)),
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/me", response_model=UserPublic, summary="当前用户")
async def get_me(
    token: str | None = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """获取当前登录用户信息。"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = session.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
