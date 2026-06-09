"""时间戳转换。"""
from __future__ import annotations

from datetime import datetime, timezone

from app.routers.schemas import TimestampOut


def convert(timestamp: int | None = None, datetime_str: str | None = None) -> TimestampOut:
    """时间戳 ↔ 时间字符串 互转。"""
    if timestamp is not None:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    elif datetime_str:
        try:
            # 尝试 ISO 格式
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        except ValueError:
            # 尝试常见格式
            for fmt in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d",
            ):
                try:
                    dt = datetime.strptime(datetime_str, fmt).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"无法解析时间字符串: {datetime_str!r}") from None
    else:
        # 默认当前时间
        dt = datetime.now(timezone.utc)

    return TimestampOut(
        timestamp=int(dt.timestamp()),
        iso=dt.isoformat(),
        utc=dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
        local=dt.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
    )
