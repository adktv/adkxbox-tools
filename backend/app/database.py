"""数据库连接 + session 管理。"""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# SQLite 需要 check_same_thread=False
connect_args: dict[str, Any] = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args,
    pool_pre_ping=True,
)


def init_db() -> None:
    """初始化所有表（dev 用，生产用 alembic）。"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI 依赖：提供 DB session。"""
    with Session(engine) as session:
        yield session
