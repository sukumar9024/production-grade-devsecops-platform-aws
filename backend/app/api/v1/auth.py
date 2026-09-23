from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
)from sqlalchemy.orm import Session
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
from app.core.audit_actions import AuditActions
from app.core.request_context import (
    get_client_ip,
    get_request_id,
)
from app.services.audit_service import AuditService

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
    request: Request,
    db: Session = Depends(get_db),
) -> UserResponse:
    user = AuthService.register_user(
        db=db,
        payload=payload,
    )

    AuditService.record(
        db=db,
        action=AuditActions.USER_REGISTERED,
        resource_type="user",
        user_id=user.id,
        resource_id=str(user.id),
        request_id=get_request_id(request),
        ip_address=get_client_ip(request),
        details={
            "username": user.username,
            "email": user.email,
        },
    )

    return user

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