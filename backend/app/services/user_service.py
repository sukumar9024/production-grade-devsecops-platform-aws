import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.roles import Roles
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    def list_users(
        db: Session,
    ) -> list[User]:
        return UserRepository.get_all(db)

    @staticmethod
    def get_user(
        db: Session,
        user_id: uuid.UUID,
    ) -> User:
        user = UserRepository.get_by_id(
            db=db,
            user_id=user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        return user

    @staticmethod
    def update_role(
        db: Session,
        user_id: uuid.UUID,
        role_name: str,
    ) -> User:
        if role_name not in Roles.ALL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role.",
            )

        user = UserService.get_user(
            db=db,
            user_id=user_id,
        )

        role = RoleRepository.get_by_name(
            db=db,
            name=role_name,
        )

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role configuration is missing.",
            )

        AuditLogRepository.stage(db, "user.role.changed", "user", user.id)
        user.role_id = role.id
        user.role = role

        return UserRepository.save(
            db=db,
            user=user,
        )

    @staticmethod
    def update_status(
        db: Session,
        user_id: uuid.UUID,
        user_status: UserStatus,
    ) -> User:
        user = UserService.get_user(
            db=db,
            user_id=user_id,
        )

        AuditLogRepository.stage(db, "user.status.changed", "user", user.id)
        user.status = user_status

        return UserRepository.save(
            db=db,
            user=user,
        )
