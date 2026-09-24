import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    @staticmethod
    def record(
        db: Session,
        action: str,
        resource_type: str,
        user_id=None,
        resource_id=None,
        request_id=None,
        ip_address=None,
        details=None,
    ) -> AuditLog:
        return AuditLogRepository.create(
            db,
            AuditLog(
                action=action,
                resource_type=resource_type,
                user_id=user_id,
                resource_id=resource_id,
                request_id=request_id,
                ip_address=ip_address,
                details=details,
            ),
        )

    @staticmethod
    def get_audit_log(db: Session, audit_log_id: uuid.UUID) -> AuditLog:
        audit_log = AuditLogRepository.get_by_id(db, audit_log_id)
        if audit_log is None:
            raise HTTPException(status_code=404, detail="Audit log not found.")
        return audit_log

    @staticmethod
    def list_audit_logs(
        db: Session,
        offset: int,
        limit: int,
        user_id=None,
        action=None,
        resource_type=None,
    ) -> list[AuditLog]:
        return AuditLogRepository.get_all(
            db, offset, limit, user_id, action, resource_type
        )
