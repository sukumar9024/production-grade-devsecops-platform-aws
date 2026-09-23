import uuid

import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
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
    
    @staticmethod
    def login(
        db: Session,
        identity: str,
        password: str,
    ) -> TokenResponse:
        user = UserRepository.get_by_login(
            db=db,
            identity=identity,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )

        if user.status.value != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled.",
            )

        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role.name,
        )

        refresh_token, jti, expires_at = (
            create_refresh_token(
                user_id=str(user.id)
            )
        )

        token_record = RefreshToken(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
        )

        RefreshTokenRepository.create(
            db=db,
            token=token_record,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str,
    ) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)

        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
            )

        jti = payload.get("jti")
        user_id = payload.get("sub")

        if not jti or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        stored_token = (
            RefreshTokenRepository.get_by_jti(
                db=db,
                jti=jti,
            )
        )

        if (
            stored_token is None
            or stored_token.revoked
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is revoked.",
            )

        user = db.get(
            User,
            uuid.UUID(user_id),
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists.",
            )

        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role.name,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    @staticmethod
    def logout(
        db: Session,
        refresh_token: str,
    ) -> None:
        try:
            payload = decode_token(refresh_token)

        except jwt.PyJWTError:
            return

        if payload.get("type") != "refresh":
            return

        jti = payload.get("jti")

        if not jti:
            return

        stored_token = (
            RefreshTokenRepository.get_by_jti(
                db=db,
                jti=jti,
            )
        )

        if stored_token is None:
            return

        if not stored_token.revoked:
            RefreshTokenRepository.revoke(
                db=db,
                token=stored_token,
            )