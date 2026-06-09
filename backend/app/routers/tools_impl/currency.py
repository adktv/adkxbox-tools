"""货币换算 - 使用 exchangerate-api.com 免费接口。"""
from __future__ import annotations

import time
from typing import Optional

import httpx
from pydantic import BaseModel, Field

_CACHE: dict[str, tuple[float, dict[str, float]]] = {}
_CACHE_TTL = 3600  # 1 小时
_API_URL = "https://api.exchangerate-api.com/v4/latest/{base}"


class CurrencyIn(BaseModel):
    from_currency: str = Field(min_length=3, max_length=3, description="源币种代码")
    to_currency: str = Field(min_length=3, max_length=3, description="目标币种代码")
    amount: float = Field(default=1.0, gt=0)


class CurrencyOut(BaseModel):
    from_currency: str
    to_currency: str
    amount: float
    rate: float
    converted: float
    timestamp: str
    cached: bool


async def _fetch_rates(base: str) -> dict[str, float]:
    """从 API 获取汇率（带缓存）。"""
    base = base.upper()
    now = time.time()

    if base in _CACHE:
        ts, rates = _CACHE[base]
        if now - ts < _CACHE_TTL:
            return rates

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(_API_URL.format(base=base))
        resp.raise_for_status()
        data = resp.json()
        rates: dict[str, float] = data.get("rates", {})
        _CACHE[base] = (now, rates)
        return rates


async def convert(data: CurrencyIn) -> CurrencyOut:
    """换算货币。"""
    from_cur = data.from_currency.upper()
    to_cur = data.to_currency.upper()

    if from_cur == to_cur:
        return CurrencyOut(
            from_currency=from_cur,
            to_currency=to_cur,
            amount=data.amount,
            rate=1.0,
            converted=data.amount,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            cached=False,
        )

    rates = await _fetch_rates(from_cur)
    if to_cur not in rates:
        raise ValueError(f"不支持的币种: {to_cur!r}")

    rate = rates[to_cur]
    converted = data.amount * rate
    cached = from_cur in _CACHE and (time.time() - _CACHE[from_cur][0]) < _CACHE_TTL

    return CurrencyOut(
        from_currency=from_cur,
        to_currency=to_cur,
        amount=data.amount,
        rate=round(rate, 6),
        converted=round(converted, 4),
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        cached=cached,
    )
