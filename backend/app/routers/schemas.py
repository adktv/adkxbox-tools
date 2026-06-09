"""工具路由的请求/响应 Pydantic 模型（独立模块避免循环引用）。"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ============= 通用 =============
class TextIn(BaseModel):
    text: str = Field(..., description="输入文本")


class TextOut(BaseModel):
    result: str


# ============= JSON =============
class JsonFormatIn(BaseModel):
    text: str
    indent: int = 2
    sort_keys: bool = False


class JsonFormatOut(BaseModel):
    result: str
    valid: bool


# ============= 正则 =============
class RegexIn(BaseModel):
    pattern: str
    text: str
    flags: str = ""


class RegexMatch(BaseModel):
    match: str
    start: int
    end: int
    groups: list[str] = []


class RegexOut(BaseModel):
    valid: bool
    error: str | None = None
    matches: list[RegexMatch]


# ============= 时间戳 =============
class TimestampIn(BaseModel):
    timestamp: int | None = None
    datetime_str: str | None = None


class TimestampOut(BaseModel):
    timestamp: int
    iso: str
    utc: str
    local: str


# ============= UUID =============
class UuidIn(BaseModel):
    version: int = 4
    count: int = 1


class UuidOut(BaseModel):
    uuids: list[str]


# ============= 颜色 =============
class ColorIn(BaseModel):
    color: str


class ColorOut(BaseModel):
    hex: str
    rgb: str
    hsl: str
    rgba: str
