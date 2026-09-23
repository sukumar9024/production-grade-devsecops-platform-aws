import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.permissions import admin_only
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.services.user_service import UserService
from app.core.roles import Roles

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=list[UserResponse],
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> list[User]:
    return UserService.list_users(
        db=db,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> User:
    return UserService.get_user(
        db=db,
        user_id=user_id,
    )


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
def update_user_role(
    user_id: uuid.UUID,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_only),
) -> User:
    if (
        user_id == current_admin.id
        and payload.role != Roles.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own Admin role.",
        )

    return UserService.update_role(
        db=db,
        user_id=user_id,
        role_name=payload.role,
    )


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
)
def update_user_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_only),
) -> User:
    if (
        user_id == current_admin.id
        and payload.status.value == "disabled"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot disable your own account.",
        )

    return UserService.update_status(
        db=db,
        user_id=user_id,
        user_status=payload.status,
    )