"""数据模型。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# ============= User =============
class UserBase(SQLModel):
    """User 基础字段。"""

    username: str = Field(min_length=3, max_length=32, index=True, unique=True)
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_admin: bool = False


class User(UserBase, table=True):
    """User 数据库表。"""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(min_length=1, nullable=False)
    api_key: Optional[str] = Field(default=None, index=True, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login: Optional[datetime] = Field(default=None, nullable=True)


class UserCreate(SQLModel):
    """注册请求。"""

    username: str = Field(min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserPublic(SQLModel):
    """User 公开信息（不含密码）。"""

    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]


# ============= Tool =============
class Tool(SQLModel, table=True):
    """工具配置表（后台可管理）。"""

    __tablename__ = "tools"

    id: str = Field(primary_key=True, max_length=64)  # e.g. "base64"
    name_zh: str
    name_en: str
    description_zh: str = ""
    description_en: str = ""
    category: str = "general"
    enabled: bool = True
    order: int = 0
    is_new: bool = False
    is_featured: bool = False  # 大哥定制的特色工具
    config: str = "{}"  # JSON 字符串


class ToolPublic(SQLModel):
    """工具公开信息。"""

    id: str
    name_zh: str
    name_en: str
    description_zh: str
    description_en: str
    category: str
    enabled: bool
    order: int
    is_new: bool
    is_featured: bool
