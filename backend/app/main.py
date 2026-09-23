import logging 
from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.api.health import router as health_router
from app.middleware.metrics import (
    MetricsMiddleware,
)
from app.api.metrics import (
    router as metrics_router,
)
from contextlib import asynccontextmanager
from app.core.logging import configure_logging
from app.middleware.request_logging import (
    RequestLoggingMiddleware,
)

configure_logging()

logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    application.include_router(
        api_v1_router,
        prefix=settings.api_v1_prefix,
    )

    application.include_router(
    api_v1_router,
    prefix=settings.api_v1_prefix,
    )

    application.include_router(
        health_router,
    )
    application.add_middleware(
    MetricsMiddleware
    )
    application.include_router(
    metrics_router,
    )

    application.add_middleware(
    RequestLoggingMiddleware
    )

    return application


app = create_application()


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }

@asynccontextmanager
async def lifespan(
    application: FastAPI,
):
    logger.info(
        "Application starting",
        extra={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
        },
    )

    yield

    logger.info(
        "Application stopping"
    )

application = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)