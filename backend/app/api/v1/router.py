from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.users import router as users_router
from app.api.v1.services import router as services_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(projects_router)
router.include_router(services_router)

@router.get("/")
async def api_v1_root() -> dict[str, str]:
    return {
        "message": "SecureOps API v1",
    }