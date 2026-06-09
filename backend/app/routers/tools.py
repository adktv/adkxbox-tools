"""工具执行路由 - 客户端工具 + 服务端工具。

注：@limiter.limit 在 SQLModel 字段返回的路由上会触发 500（slowapi 0.1.x + FastAPI 0.115
+ SQLModel/Pydantic v2 字段访问的兼容 bug）。工具路由限流改在 Caddy 层用 rate_limit
中间件代替（见 /etc/caddy/Caddyfile 的 :18991 block）。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.routers.schemas import (
    ColorIn,
    ColorOut,
    JsonFormatIn,
    JsonFormatOut,
    RegexIn,
    RegexOut,
    TextIn,
    TextOut,
    TimestampIn,
    TimestampOut,
    UuidIn,
    UuidOut,
)
from app.routers.tools_impl import base64_tool, color_picker, currency, iptv_probe, json_tool
from app.routers.tools_impl import regex_tool, timestamp_tool, url_tool, uuid_tool, vps_calculator

router = APIRouter()


# ============= 客户端工具 =============
@router.post("/base64/encode", response_model=TextOut, summary="Base64 编码")
async def base64_encode(data: TextIn) -> TextOut:
    return TextOut(result=base64_tool.encode(data.text))


@router.post("/base64/decode", response_model=TextOut, summary="Base64 解码")
async def base64_decode(data: TextIn) -> TextOut:
    try:
        return TextOut(result=base64_tool.decode(data.text))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Base64 解码失败: {e!s}") from e


@router.post("/url/encode", response_model=TextOut, summary="URL 编码")
async def url_encode(data: TextIn) -> TextOut:
    return TextOut(result=url_tool.encode(data.text))


@router.post("/url/decode", response_model=TextOut, summary="URL 解码")
async def url_decode(data: TextIn) -> TextOut:
    try:
        return TextOut(result=url_tool.decode(data.text))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"URL 解码失败: {e!s}") from e


@router.post("/json/format", response_model=JsonFormatOut, summary="JSON 格式化")
async def json_format(data: JsonFormatIn) -> JsonFormatOut:
    return json_tool.format(data.text, data.indent, data.sort_keys)


@router.post("/regex/match", response_model=RegexOut, summary="正则匹配")
async def regex_match(data: RegexIn) -> RegexOut:
    return regex_tool.match(data.pattern, data.text, data.flags)


@router.post("/timestamp/convert", response_model=TimestampOut, summary="时间戳 ↔ 时间字符串")
async def timestamp_convert(data: TimestampIn) -> TimestampOut:
    return timestamp_tool.convert(data.timestamp, data.datetime_str)


@router.post("/uuid/generate", response_model=UuidOut, summary="UUID 生成")
async def uuid_generate(data: UuidIn) -> UuidOut:
    return UuidOut(uuids=uuid_tool.generate(data.version, min(data.count, 100)))


@router.post("/color/convert", response_model=ColorOut, summary="颜色格式转换")
async def color_convert(data: ColorIn) -> ColorOut:
    return color_picker.convert(data.color)


# ============= 服务端工具（特色）====================
@router.post("/vps-calculator/calc", summary="VPS 剩余价值计算")
async def vps_calc(data: vps_calculator.VpsCalcIn) -> vps_calculator.VpsCalcOut:
    return vps_calculator.calc(data)


@router.post("/currency/convert", summary="实时货币换算")
async def currency_convert(data: currency.CurrencyIn) -> currency.CurrencyOut:
    return await currency.convert(data)


@router.post("/iptv-probe", summary="IPTV 频道延迟测试")
async def iptv_probe_endpoint(data: iptv_probe.ProbeIn) -> iptv_probe.ProbeOut:
    return await iptv_probe.probe(data)
