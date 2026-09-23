import uuid

from fastapi import HTTPException, status


@staticmethod
def get_audit_log(
    db: Session,
    audit_log_id: uuid.UUID,
) -> AuditLog:
    audit_log = (
        AuditLogRepository.get_by_id(
            db=db,
            audit_log_id=audit_log_id,
        )
    )

    if audit_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found.",
        )

    return audit_log


@staticmethod
def list_audit_logs(
    db: Session,
    offset: int,
    limit: int,
    user_id: uuid.UUID | None,
    action: str | None,
    resource_type: str | None,
) -> list[AuditLog]:
    return AuditLogRepository.get_all(
        db=db,
        offset=offset,
        limit=limit,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
    )