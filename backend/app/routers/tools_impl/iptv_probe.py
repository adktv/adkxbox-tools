"""IPTV 频道探针。

对 HLS/m3u8 频道做延迟/可用性测试。
"""
from __future__ import annotations

import time
from typing import Optional

import httpx
from pydantic import BaseModel, Field


class ProbeIn(BaseModel):
    url: str = Field(description="HLS/m3u8 URL")
    timeout: float = Field(default=8.0, ge=1, le=30)
    test_segments: int = Field(default=3, ge=1, le=10, description="测试分片数")


class ProbeSegment(BaseModel):
    segment_url: str
    status: int
    duration_ms: float
    size_bytes: int
    error: Optional[str] = None


class ProbeOut(BaseModel):
    url: str
    reachable: bool
    playlist_status: Optional[int] = None
    playlist_duration_ms: Optional[float] = None
    segments: list[ProbeSegment] = []
    avg_segment_ms: Optional[float] = None
    total_bandwidth_kbps: Optional[float] = None
    error: Optional[str] = None


async def _probe_segment(client: httpx.AsyncClient, url: str, timeout: float) -> ProbeSegment:
    """探测单个分片。"""
    start = time.time()
    try:
        resp = await client.get(url, timeout=timeout, follow_redirects=True)
        duration = (time.time() - start) * 1000
        return ProbeSegment(
            segment_url=url,
            status=resp.status_code,
            duration_ms=round(duration, 2),
            size_bytes=len(resp.content),
            error=None if resp.status_code == 200 else f"HTTP {resp.status_code}",
        )
    except Exception as e:  # noqa: BLE001
        duration = (time.time() - start) * 1000
        return ProbeSegment(
            segment_url=url,
            status=0,
            duration_ms=round(duration, 2),
            size_bytes=0,
            error=str(e),
        )


async def probe(data: ProbeIn) -> ProbeOut:
    """测试 HLS 流可用性和延迟。"""
    out = ProbeOut(url=data.url, reachable=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        # 1. 拉 m3u8 playlist
        playlist_start = time.time()
        try:
            resp = await client.get(data.url, timeout=data.timeout, follow_redirects=True)
        except Exception as e:  # noqa: BLE001
            out.error = f"无法获取 playlist: {e!s}"
            return out

        out.playlist_status = resp.status_code
        out.playlist_duration_ms = round((time.time() - playlist_start) * 1000, 2)

        if resp.status_code != 200:
            out.error = f"playlist HTTP {resp.status_code}"
            return out

        out.reachable = True
        playlist = resp.text

        # 2. 解析 m3u8 找 ts 分片
        lines = playlist.strip().split("\n")
        base_url = data.url.rsplit("/", 1)[0] + "/"
        ts_urls: list[str] = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and (line.endswith(".ts") or ".ts?" in line):
                if line.startswith("http"):
                    ts_urls.append(line)
                else:
                    ts_urls.append(base_url + line)

        if not ts_urls:
            out.error = "未在 playlist 中找到 .ts 分片（非 HLS？）"
            return out

        # 3. 测前 N 个分片
        for ts in ts_urls[: data.test_segments]:
            seg = await _probe_segment(client, ts, data.timeout)
            out.segments.append(seg)

        # 4. 统计
        success = [s for s in out.segments if s.status == 200]
        if success:
            total_ms = sum(s.duration_ms for s in success)
            total_bytes = sum(s.size_bytes for s in success)
            out.avg_segment_ms = round(total_ms / len(success), 2)
            # 估算带宽 (kbps) - 假设每个分片是 6 秒视频
            if total_ms > 0:
                bits = total_bytes * 8
                seconds = total_ms / 1000
                out.total_bandwidth_kbps = round(bits / seconds / 1000, 2)
        else:
            out.error = "所有分片探测失败"

    return out
