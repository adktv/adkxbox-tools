"""颜色格式转换 (HEX / RGB / HSL / RGBA)。"""
from __future__ import annotations

import re
from colorsys import hls_to_rgb, rgb_to_hls

from app.routers.schemas import ColorOut


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"无效的 HEX 颜色: {hex_str!r}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _parse_rgb(text: str) -> tuple[int, int, int, float | None]:
    """解析 rgb() 或 rgba() 字符串。"""
    m = re.match(
        r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)",
        text.strip(),
    )
    if not m:
        raise ValueError(f"无法解析 RGB 颜色: {text!r}")
    r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
    a = float(m.group(4)) if m.group(4) else None
    return r, g, b, a


def _parse_hsl(text: str) -> tuple[int, int, int]:
    """解析 hsl() 字符串。"""
    m = re.match(
        r"hsla?\s*\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*(?:,\s*[\d.]+\s*)?\)",
        text.strip(),
    )
    if not m:
        raise ValueError(f"无法解析 HSL 颜色: {text!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def convert(color: str) -> ColorOut:
    """转换颜色格式。"""
    color = color.strip()
    if color.startswith("#"):
        r, g, b = _hex_to_rgb(color)
    elif color.lower().startswith("rgb"):
        r, g, b, _ = _parse_rgb(color)
    elif color.lower().startswith("hsl"):
        h, s, l = _parse_hsl(color)
        r, g, b = (round(c * 255) for c in hls_to_rgb(h / 360, l / 100, s / 100))
    else:
        raise ValueError(f"不支持的颜色格式: {color!r}")

    h, l, s = rgb_to_hls(r / 255, g / 255, b / 255)
    return ColorOut(
        hex=_rgb_to_hex(r, g, b),
        rgb=f"rgb({r}, {g}, {b})",
        rgba=f"rgba({r}, {g}, {b}, 1)",
        hsl=f"hsl({round(h * 360)}, {round(s * 100)}%, {round(l * 100)}%)",
    )
