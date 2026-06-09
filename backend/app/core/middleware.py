"""自定义 IP 限流中间件（纯 ASGI，避免 BaseHTTPMiddleware 截断 response）。

- sliding window, 内存存储
- /api/auth/*  10 req/min/IP（防爆破）
- /api/tools/* 60 req/min/IP
- 本地 IP 白名单
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

# Starlette / FastAPI 用的 ASGI 接口
RULES: Dict[str, Tuple[int, int]] = {
    "/api/auth/": (10, 60),
    "/api/tools/": (60, 60),
}

# 内存存储: ip -> path_prefix -> deque[timestamp]
_STORE: Dict[str, Dict[str, Deque[float]]] = defaultdict(lambda: defaultdict(deque))

WHITELIST = {"127.0.0.1", "::1", "localhost"}


def _client_ip(scope: dict) -> str:
    headers = dict(scope.get("headers") or [])
    xff = headers.get(b"x-forwarded-for")
    if xff:
        return xff.decode("latin-1").split(",")[0].strip()
    xri = headers.get(b"x-real-ip")
    if xri:
        return xri.decode("latin-1").strip()
    client = scope.get("client")
    return client[0] if client else "unknown"


def _check(ip: str, path: str) -> Tuple[bool, int, int, int, int]:
    """返回 (allowed, limit, window, remaining, retry_after)。"""
    for prefix, (limit, window) in RULES.items():
        if path.startswith(prefix):
            now = time.time()
            store = _STORE[ip][prefix]
            cutoff = now - window
            while store and store[0] < cutoff:
                store.popleft()
            if len(store) >= limit:
                retry = int(window - (now - store[0])) + 1
                return False, limit, window, 0, retry
            store.append(now)
            return True, limit, window, limit - len(store), 0
    return True, 0, 0, 0, 0


class IPRateLimitMiddleware:
    """纯 ASGI 中间件 - IP 限流"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        ip = _client_ip(scope)
        if ip in WHITELIST:
            await self.app(scope, receive, send)
            return

        allowed, limit, window, remaining, retry = _check(ip, path)
        headers_extra = []
        if limit > 0:
            headers_extra.extend(
                [
                    (b"x-ratelimit-limit", str(limit).encode()),
                    (b"x-ratelimit-remaining", str(max(0, remaining)).encode()),
                ]
            )

        if not allowed:
            body = (
                f'{{"detail":"Rate limit exceeded","limit":{limit},'
                f'"window_seconds":{window},"retry_after":{retry}}}'
            ).encode("utf-8")
            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode()),
                        (b"retry-after", str(retry).encode()),
                        (b"x-ratelimit-limit", str(limit).encode()),
                        (b"x-ratelimit-remaining", b"0"),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body, "more_body": False})
            return

        # 透传 + 注入 header
        async def send_wrapper(message):
            if message["type"] == "http.response.start" and limit > 0:
                hdrs = list(message.get("headers", []))
                hdrs.extend(headers_extra)
                message["headers"] = hdrs
            await send(message)

        await self.app(scope, receive, send_wrapper)
