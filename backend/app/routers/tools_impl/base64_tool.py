"""Base64 编/解码。"""
from __future__ import annotations

import base64 as b64


def encode(text: str) -> str:
    """Base64 编码。"""
    return b64.b64encode(text.encode("utf-8")).decode("ascii")


def decode(text: str) -> str:
    """Base64 解码。"""
    return b64.b64decode(text.encode("ascii")).decode("utf-8")
