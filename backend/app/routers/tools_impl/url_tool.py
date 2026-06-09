"""URL 编/解码。"""
from __future__ import annotations

import urllib.parse


def encode(text: str) -> str:
    return urllib.parse.quote(text, safe="")


def decode(text: str) -> str:
    return urllib.parse.unquote(text)
