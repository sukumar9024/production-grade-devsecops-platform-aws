from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings


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

    return application


app = create_application()


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }