"""正则表达式测试。"""
from __future__ import annotations

import re

from app.routers.schemas import RegexMatch, RegexOut

_FLAG_MAP = {
    "i": re.IGNORECASE,
    "m": re.MULTILINE,
    "s": re.DOTALL,
    "x": re.VERBOSE,
    "a": re.ASCII,
}


def _parse_flags(flags_str: str) -> re.RegexFlag:
    """解析 flags 字符串。"""
    flag = re.RegexFlag(0)
    for ch in flags_str.lower():
        if ch in _FLAG_MAP:
            flag |= _FLAG_MAP[ch]
    return flag


def match(pattern: str, text: str, flags: str = "") -> RegexOut:
    """执行正则匹配。"""
    try:
        compiled = re.compile(pattern, _parse_flags(flags))
        matches: list[RegexMatch] = []
        for m in compiled.finditer(text):
            matches.append(
                RegexMatch(
                    match=m.group(0),
                    start=m.start(),
                    end=m.end(),
                    groups=list(m.groups()) if m.groups() else [],
                )
            )
        return RegexOut(valid=True, error=None, matches=matches)
    except re.error as e:
        return RegexOut(valid=False, error=str(e), matches=[])
    except Exception as e:  # noqa: BLE001
        return RegexOut(valid=False, error=str(e), matches=[])
