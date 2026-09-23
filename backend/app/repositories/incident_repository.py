import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import (
    IncidentSeverity,
    IncidentStatus,
)
from app.models.incident import Incident


class IncidentRepository:
    @staticmethod
    def get_by_id(
        db: Session,
        incident_id: uuid.UUID,
    ) -> Incident | None:
        statement = (
            select(Incident)
            .options(
                joinedload(Incident.service)
            )
            .where(
                Incident.id == incident_id
            )
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        offset: int,
        limit: int,
        service_id: uuid.UUID | None = None,
        incident_status: IncidentStatus | None = None,
        severity: IncidentSeverity | None = None,
    ) -> list[Incident]:
        statement = (
            select(Incident)
            .options(
                joinedload(Incident.service)
            )
            .order_by(
                Incident.detected_at.desc()
            )
        )

        if service_id is not None:
            statement = statement.where(
                Incident.service_id == service_id
            )

        if incident_status is not None:
            statement = statement.where(
                Incident.status == incident_status
            )

        if severity is not None:
            statement = statement.where(
                Incident.severity == severity
            )

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def create(
        db: Session,
        incident: Incident,
    ) -> Incident:
        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident

    @staticmethod
    def save(
        db: Session,
        incident: Incident,
    ) -> Incident:
        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident