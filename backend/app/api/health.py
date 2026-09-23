from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

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
    return LivenessResponse(
        status="alive"
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
)
def readiness(
    response: Response,
    db: Session = Depends(get_db),
) -> ReadinessResponse:
    database = HealthService.check_database(
        db=db
    )

    if database.status != "healthy":
        response.status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return ReadinessResponse(
            status="not_ready",
            database=database,
        )

    return ReadinessResponse(
        status="ready",
        database=database,
    )