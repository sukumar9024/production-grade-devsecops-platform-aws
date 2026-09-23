from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def api_v1_root() -> dict[str, str]:
    return {
        "message": "SecureOps API v1",
    }