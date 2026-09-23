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
from app.models.enums import DeploymentStatus
from app.models.user import User
from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentResponse,
    DeploymentUpdate,
)
from app.services.deployment_service import (
    DeploymentService,
)


router = APIRouter(
    prefix="/deployments",
    tags=["Deployments"],
)


@router.post(
    "",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_deployment(
    payload: DeploymentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        engineer_or_admin
    ),
) -> DeploymentResponse:
    return DeploymentService.create_deployment(
        db=db,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[DeploymentResponse],
)
def list_deployments(
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
    deployment_status: DeploymentStatus | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(
        authenticated_user
    ),
) -> list[DeploymentResponse]:
    return DeploymentService.list_deployments(
        db=db,
        offset=offset,
        limit=limit,
        service_id=service_id,
        deployment_status=deployment_status,
    )


@router.get(
    "/{deployment_id}",
    response_model=DeploymentResponse,
)
def get_deployment(
    deployment_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(
        authenticated_user
    ),
) -> DeploymentResponse:
    return DeploymentService.get_deployment(
        db=db,
        deployment_id=deployment_id,
    )


@router.patch(
    "/{deployment_id}",
    response_model=DeploymentResponse,
)
def update_deployment(
    deployment_id: uuid.UUID,
    payload: DeploymentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(
        engineer_or_admin
    ),
) -> DeploymentResponse:
    return DeploymentService.update_deployment(
        db=db,
        deployment_id=deployment_id,
        payload=payload,
    )