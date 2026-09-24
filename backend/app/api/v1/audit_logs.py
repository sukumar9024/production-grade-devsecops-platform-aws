import uuid

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.permissions import admin_only
from app.models.user import User
from app.schemas.audit_log import (
    AuditLogResponse,
)
from app.services.audit_service import (
    AuditService,
)

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "",
    response_model=list[AuditLogResponse],
)
def list_audit_logs(
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    user_id: uuid.UUID | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> list[AuditLogResponse]:
    return AuditService.list_audit_logs(
        db=db,
        offset=offset,
        limit=limit,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
    )


@router.get(
    "/{audit_log_id}",
    response_model=AuditLogResponse,
)
def get_audit_log(
    audit_log_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> AuditLogResponse:
    return AuditService.get_audit_log(
        db=db,
        audit_log_id=audit_log_id,
    )
