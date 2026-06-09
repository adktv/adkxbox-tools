"""健康检查 + 工具清单。"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlmodel import Session

from app.config import settings
from app.database import get_session
from app.models import Tool, ToolPublic

router = APIRouter()


@router.get("/health", summary="健康检查")
async def health() -> dict:
    """服务健康检查。"""
    return {
        "status": "ok",
        "service": settings.api_title,
        "version": settings.api_version,
        "env": settings.env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/tools", response_model=list[ToolPublic], summary="工具清单")
async def list_tools(session: Session = Depends(get_session)) -> list[Tool]:
    """获取所有启用的工具列表。"""
    statement = (
        select(Tool)
        .where(Tool.enabled == True)  # noqa: E712
        .order_by(Tool.order, Tool.id)
    )
    return list(session.exec(statement).all())
