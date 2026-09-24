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
    admin_only,
    authenticated_user,
    engineer_or_admin,
)
from app.models.enums import Environment
from app.models.user import User
from app.schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from app.services.service_service import ServiceService

router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(engineer_or_admin),
) -> ServiceResponse:
    return ServiceService.create_service(
        db=db,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[ServiceResponse],
)
def list_services(
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    project_id: uuid.UUID | None = None,
    environment: Environment | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(authenticated_user),
) -> list[ServiceResponse]:
    return ServiceService.list_services(
        db=db,
        offset=offset,
        limit=limit,
        project_id=project_id,
        environment=environment,
    )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
def get_service(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(authenticated_user),
) -> ServiceResponse:
    return ServiceService.get_service(
        db=db,
        service_id=service_id,
    )


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
)
def update_service(
    service_id: uuid.UUID,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(engineer_or_admin),
) -> ServiceResponse:
    return ServiceService.update_service(
        db=db,
        service_id=service_id,
        payload=payload,
    )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> None:
    ServiceService.delete_service(
        db=db,
        service_id=service_id,
    )
