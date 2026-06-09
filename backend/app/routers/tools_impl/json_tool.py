"""JSON 格式化 / 验证。"""
from __future__ import annotations

import json

from app.routers.schemas import JsonFormatOut


def format(text: str, indent: int = 2, sort_keys: bool = False) -> JsonFormatOut:
    """格式化 JSON。"""
    try:
        data = json.loads(text)
        result = json.dumps(
            data,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=False,
        )
        return JsonFormatOut(result=result, valid=True)
    except json.JSONDecodeError as e:
        return JsonFormatOut(result=text, valid=False)  # type: ignore[return-value]
    except Exception as e:  # noqa: BLE001
        return JsonFormatOut(result=f"Error: {e}", valid=False)  # type: ignore[return-value]
