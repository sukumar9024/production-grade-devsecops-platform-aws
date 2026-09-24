import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.request_context import get_current_request_id
from app.models.audit_log import AuditLog


class AuditLogRepository:
    @staticmethod
    def stage(
        db: Session, action: str, resource_type: str, resource_id=None, user_id=None
    ) -> AuditLog:
        """Stage an event in the same transaction as the business operation."""
        event = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            user_id=user_id if user_id is not None else db.info.get("actor_id"),
            request_id=get_current_request_id(),
            ip_address=db.info.get("client_ip"),
        )
        db.add(event)
        return event

    @staticmethod
    def create(
        db: Session,
        audit_log: AuditLog,
    ) -> AuditLog:
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    def get_by_id(
        db: Session,
        audit_log_id: uuid.UUID,
    ) -> AuditLog | None:
        statement = (
            select(AuditLog)
            .options(joinedload(AuditLog.user))
            .where(AuditLog.id == audit_log_id)
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        offset: int,
        limit: int,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .options(joinedload(AuditLog.user))
            .order_by(AuditLog.created_at.desc())
        )

        if user_id is not None:
            statement = statement.where(AuditLog.user_id == user_id)

        if action is not None:
            statement = statement.where(AuditLog.action == action)

        if resource_type is not None:
            statement = statement.where(AuditLog.resource_type == resource_type)

        statement = statement.offset(offset).limit(limit)

        return list(db.scalars(statement).all())
