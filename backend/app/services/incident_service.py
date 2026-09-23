import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import IncidentStatus
from app.models.incident import Incident
from app.repositories.incident_repository import (
    IncidentRepository,
)
from app.repositories.service_repository import (
    ServiceRepository,
)
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
)


class IncidentService:
    ALLOWED_TRANSITIONS = {
        IncidentStatus.OPEN: {
            IncidentStatus.INVESTIGATING,
            IncidentStatus.RESOLVED,
        },
        IncidentStatus.INVESTIGATING: {
            IncidentStatus.RESOLVED,
        },
        IncidentStatus.RESOLVED: {
            IncidentStatus.CLOSED,
        },
        IncidentStatus.CLOSED: set(),
    }

    @staticmethod
    def create_incident(
        db: Session,
        payload: IncidentCreate,
    ) -> Incident:
        service = ServiceRepository.get_by_id(
            db=db,
            service_id=payload.service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        incident = Incident(
            service_id=payload.service_id,
            title=payload.title.strip(),
            description=payload.description.strip(),
            severity=payload.severity,
            status=IncidentStatus.OPEN,
            detected_at=datetime.now(UTC),
        )

        created_incident = (
            IncidentRepository.create(
                db=db,
                incident=incident,
            )
        )

        return IncidentRepository.get_by_id(
            db=db,
            incident_id=created_incident.id,
        )

    @staticmethod
    def list_incidents(
        db: Session,
        offset: int,
        limit: int,
        service_id: uuid.UUID | None,
        incident_status: IncidentStatus | None,
        severity,
    ) -> list[Incident]:
        return IncidentRepository.get_all(
            db=db,
            offset=offset,
            limit=limit,
            service_id=service_id,
            incident_status=incident_status,
            severity=severity,
        )

    @staticmethod
    def get_incident(
        db: Session,
        incident_id: uuid.UUID,
    ) -> Incident:
        incident = IncidentRepository.get_by_id(
            db=db,
            incident_id=incident_id,
        )

        if incident is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found.",
            )

        return incident

    @staticmethod
    def update_incident(
        db: Session,
        incident_id: uuid.UUID,
        payload: IncidentUpdate,
    ) -> Incident:
        incident = IncidentService.get_incident(
            db=db,
            incident_id=incident_id,
        )

        if (
            payload.status is not None
            and payload.status != incident.status
        ):
            allowed = (
                IncidentService.ALLOWED_TRANSITIONS.get(
                    incident.status,
                    set(),
                )
            )

            if payload.status not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Invalid incident status transition: "
                        f"{incident.status.value} -> "
                        f"{payload.status.value}"
                    ),
                )

            incident.status = payload.status

            if payload.status == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.now(UTC)

        if payload.title is not None:
            incident.title = payload.title.strip()

        if payload.description is not None:
            incident.description = (
                payload.description.strip()
            )

        if payload.severity is not None:
            incident.severity = payload.severity

        IncidentRepository.save(
            db=db,
            incident=incident,
        )

        return IncidentRepository.get_by_id(
            db=db,
            incident_id=incident.id,
        )