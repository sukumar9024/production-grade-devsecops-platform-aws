import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.audit_log import AuditLog


class AuditLogRepository:
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
            .options(
                joinedload(AuditLog.user)
            )
            .where(
                AuditLog.id == audit_log_id
            )
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
            .options(
                joinedload(AuditLog.user)
            )
            .order_by(
                AuditLog.created_at.desc()
            )
        )

        if user_id is not None:
            statement = statement.where(
                AuditLog.user_id == user_id
            )

        if action is not None:
            statement = statement.where(
                AuditLog.action == action
            )

        if resource_type is not None:
            statement = statement.where(
                AuditLog.resource_type
                == resource_type
            )

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )