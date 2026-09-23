from fastapi import APIRouter

from app.api.v1.auth import router as auth_router


router = APIRouter()


router.include_router(auth_router)


@router.get("/")
async def api_v1_root() -> dict[str, str]:
    return {
        "message": "SecureOps API v1",
    }