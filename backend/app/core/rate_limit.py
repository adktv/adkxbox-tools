"""核心模块 - 限流。"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# 限流存储：开发环境用内存；生产环境用 Redis
# 如果 REDIS_URL 指向不可用的 redis 会在第一次限流时抛 ConnectionError
_storage_uri = settings.redis_url
try:
    import redis as _redis  # noqa: F401

    # 用一个简单的 socket 测试决定用 redis 还是 memory
    import socket as _socket

    s = _socket.socket()
    s.settimeout(0.5)
    # 解析 redis://host:port/db
    from urllib.parse import urlparse

    u = urlparse(_storage_uri)
    host = u.hostname or "localhost"
    port = u.port or 6379
    try:
        s.connect((host, port))
        s.close()
        _storage = _storage_uri
    except OSError:
        _storage = "memory://"
except Exception:  # noqa: BLE001
    _storage = "memory://"


# 全局限流器
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage,
    strategy="fixed-window",
    headers_enabled=True,
)
