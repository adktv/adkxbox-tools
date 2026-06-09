"""VPS 剩余价值计算器。

参考 Woodll-Tools 的 VPS 剩余价值计算功能：
- 输入：续费金额、付费周期、起止日期、溢价
- 输出：剩余价值、按天折算、月度成本
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PayCycle(str, Enum):
    """付费周期。"""

    MONTH = "month"
    QUARTER = "quarter"
    HALF_YEAR = "half_year"
    YEAR = "year"
    TWO_YEAR = "two_year"
    THREE_YEAR = "three_year"


_CYCLE_DAYS = {
    PayCycle.MONTH: 30,
    PayCycle.QUARTER: 90,
    PayCycle.HALF_YEAR: 180,
    PayCycle.YEAR: 365,
    PayCycle.TWO_YEAR: 730,
    PayCycle.THREE_YEAR: 1095,
}


class VpsCalcIn(BaseModel):
    """VPS 计算输入。"""

    price: float = Field(gt=0, description="续费金额（原币种）")
    cycle: PayCycle = PayCycle.YEAR
    start_date: str = Field(description="开始日期 YYYY-MM-DD")
    end_date: str = Field(description="到期日期 YYYY-MM-DD")
    currency: str = Field(default="USD", description="原币种")
    premium_pct: float = Field(default=0, ge=0, le=1000, description="溢价百分比（0-1000）")
    current_date: Optional[str] = Field(default=None, description="计算日期，默认今天")


class VpsCalcOut(BaseModel):
    """VPS 计算输出。"""

    cycle: str
    cycle_days: int
    total_days: int
    days_used: int
    days_remaining: int
    price: float
    currency: str
    premium_pct: float
    # 价值
    base_value: float  # 不含溢价
    premium_value: float  # 溢价部分
    total_paid: float  # 实际支付（含溢价）
    used_value: float  # 已用价值
    remaining_value: float  # 剩余价值
    # 单价
    price_per_day: float  # 每天单价
    price_per_month: float  # 折合月单价
    # 状态
    is_expired: bool
    expiry_status: str  # "active" | "expiring" | "expired"


def _parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def calc(data: VpsCalcIn) -> VpsCalcOut:
    """计算 VPS 剩余价值。"""
    start = _parse_date(data.start_date)
    end = _parse_date(data.end_date)
    now = _parse_date(data.current_date) if data.current_date else datetime.now(timezone.utc)

    total_days = (end - start).days
    days_used = max(0, (now - start).days)
    days_remaining = max(0, (end - now).days)
    is_expired = now > end

    cycle_days = _CYCLE_DAYS[data.cycle]
    base_value = data.price
    premium_value = data.price * (data.premium_pct / 100)
    total_paid = base_value + premium_value

    # 价值按天分摊
    if total_days > 0:
        value_per_day = total_paid / total_days
        used_value = value_per_day * min(days_used, total_days)
        remaining_value = value_per_day * days_remaining
    else:
        used_value = 0.0
        remaining_value = 0.0
        value_per_day = 0.0

    # 月度折算
    price_per_month = total_paid / (total_days / 30) if total_days > 0 else 0.0

    # 状态
    if is_expired:
        status = "expired"
    elif days_remaining <= 7:
        status = "expiring"
    else:
        status = "active"

    return VpsCalcOut(
        cycle=data.cycle.value,
        cycle_days=cycle_days,
        total_days=total_days,
        days_used=days_used,
        days_remaining=days_remaining,
        price=data.price,
        currency=data.currency,
        premium_pct=data.premium_pct,
        base_value=round(base_value, 2),
        premium_value=round(premium_value, 2),
        total_paid=round(total_paid, 2),
        used_value=round(used_value, 2),
        remaining_value=round(remaining_value, 2),
        price_per_day=round(value_per_day, 4),
        price_per_month=round(price_per_month, 2),
        is_expired=is_expired,
        expiry_status=status,
    )
