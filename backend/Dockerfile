# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 依赖（利用缓存）
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install fastapi 'uvicorn[standard]' pydantic 'pydantic[email]' \
                pydantic-settings sqlmodel alembic \
                'python-jose[cryptography]' 'passlib[bcrypt]' \
                python-multipart slowapi redis httpx pyyaml

# 代码
COPY app ./app

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

EXPOSE 8000

# 启动命令（生产用 gunicorn 也行）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
