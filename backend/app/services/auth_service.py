from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    DEFAULT_ROLE = "Viewer"

    @staticmethod
    def register_user(
        db: Session,
        payload: UserCreate,
    ) -> User:
        existing_user = (
            UserRepository.get_by_email_or_username(
                db=db,
                email=payload.email.lower(),
                username=payload.username.lower(),
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A user with the supplied email "
                    "or username already exists."
                ),
            )

        role = RoleRepository.get_by_name(
            db=db,
            name=AuthService.DEFAULT_ROLE,
        )

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default user role is not configured.",
            )

        user = User(
            email=payload.email.lower(),
            username=payload.username.lower(),
            full_name=payload.full_name,
            password_hash=hash_password(
                payload.password
            ),
            role_id=role.id,
        )

        return UserRepository.create(
            db=db,
            user=user,
        )