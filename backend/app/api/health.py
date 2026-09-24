from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.request_context import get_request_id
from app.db.session import get_db
from app.schemas.health import (
    LivenessResponse,
    ReadinessResponse,
)
from app.services.health_service import HealthService

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "/live",
    response_model=LivenessResponse,
)
def liveness() -> LivenessResponse:
    return LivenessResponse(status="alive")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
)
def readiness(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> ReadinessResponse:
    database = HealthService.check_database(db=db)

    redis = HealthService.check_redis()
    ready = database.status == "healthy" and redis.status == "healthy"
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        database=database,
        redis=redis,
        request_id=get_request_id(request),
    )
