from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user
    
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    return AuthService.register_user(
        db=db,
        payload=payload,
    )

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return AuthService.login(
        db=db,
        identity=payload.identity,
        password=payload.password,
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_token(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return AuthService.refresh_access_token(
        db=db,
        refresh_token=payload.refresh_token,
    )

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
) -> None:
    AuthService.logout(
        db=db,
        refresh_token=payload.refresh_token,
    )