import uuid

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.permissions import (
    authenticated_user,
    engineer_or_admin,
)
from app.models.enums import (
    IncidentSeverity,
    IncidentStatus,
)
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)
from app.services.incident_service import (
    IncidentService,
)


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        engineer_or_admin
    ),
) -> IncidentResponse:
    return IncidentService.create_incident(
        db=db,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[IncidentResponse],
)
def list_incidents(
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    service_id: uuid.UUID | None = None,
    incident_status: IncidentStatus | None = None,
    severity: IncidentSeverity | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(
        authenticated_user
    ),
) -> list[IncidentResponse]:
    return IncidentService.list_incidents(
        db=db,
        offset=offset,
        limit=limit,
        service_id=service_id,
        incident_status=incident_status,
        severity=severity,
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(
        authenticated_user
    ),
) -> IncidentResponse:
    return IncidentService.get_incident(
        db=db,
        incident_id=incident_id,
    )


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def update_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(
        engineer_or_admin
    ),
) -> IncidentResponse:
    return IncidentService.update_incident(
        db=db,
        incident_id=incident_id,
        payload=payload,
    )
    