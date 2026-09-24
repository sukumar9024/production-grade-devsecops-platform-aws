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
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import (
    ProjectService,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(engineer_or_admin),
) -> ProjectResponse:
    return ProjectService.create_project(
        db=db,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def list_projects(
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    _: User = Depends(authenticated_user),
) -> list[ProjectResponse]:
    return ProjectService.list_projects(
        db=db,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(authenticated_user),
) -> ProjectResponse:
    return ProjectService.get_project(
        db=db,
        project_id=project_id,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(engineer_or_admin),
) -> ProjectResponse:
    return ProjectService.update_project(
        db=db,
        project_id=project_id,
        payload=payload,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> None:
    ProjectService.delete_project(
        db=db,
        project_id=project_id,
    )
