"""UUID 生成。"""
from __future__ import annotations

import uuid


def generate(version: int = 4, count: int = 1) -> list[str]:
    """生成 UUID。

    Python 3.14+ 支持 uuid7，否则降级为 uuid4。
    """
    version = max(1, min(version, 7))
    if version == 1:
        return [str(uuid.uuid1()) for _ in range(count)]
    if version == 7 and hasattr(uuid, "uuid7"):
        return [str(uuid.uuid7()) for _ in range(count)]
    return [str(uuid.uuid4()) for _ in range(count)]
