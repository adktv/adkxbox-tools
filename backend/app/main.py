"""adkxbox-tools 后端应用入口。"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.rate_limit import limiter
from app.database import init_db
from app.routers import auth, health, tools

# 日志配置
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """应用工厂。"""
    app = FastAPI(
        title="adkxbox-tools API",
        description="面向开发者 / IT 从业者的在线工具箱 API",
        version="0.1.0",
        docs_url="/docs" if settings.debug else "/docs",
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json",
    )

    # CORS（生产收紧）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 限流
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # 路由
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(tools.router, prefix="/api/tools", tags=["tools"])

    @app.on_event("startup")
    async def startup_event() -> None:
        init_db()
        logger.info("🚀 adkxbox-tools API 启动")
        logger.info(f"   ENV: {settings.env}")
        logger.info(f"   Debug: {settings.debug}")
        logger.info(f"   CORS: {settings.cors_origins_list}")

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        logger.info("👋 adkxbox-tools API 关闭")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
