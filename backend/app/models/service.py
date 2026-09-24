from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import Environment, ServiceStatus

if TYPE_CHECKING:
    from app.models.deployment import Deployment
    from app.models.incident import Incident
    from app.models.project import Project


class Service(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "services"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "name",
            "environment",
            name="uq_service_project_name_environment",
        ),
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    environment: Mapped[Environment] = mapped_column(
        Enum(
            Environment,
            name="environment",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=False,
        index=True,
    )

    version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[ServiceStatus] = mapped_column(
        Enum(
            ServiceStatus,
            name="service_status",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=False,
        default=ServiceStatus.UNKNOWN,
        index=True,
    )

    health_check_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    project: Mapped[Project] = relationship(
        back_populates="services",
    )

    deployments: Mapped[list[Deployment]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
    )

    incidents: Mapped[list[Incident]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
    )
