from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DeploymentStatus


class Deployment(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "deployments"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "services.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    git_commit: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    image_digest: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    pipeline_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    status: Mapped[DeploymentStatus] = mapped_column(
        Enum(
            DeploymentStatus,
            name="deployment_status",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=False,
        default=DeploymentStatus.PENDING,
        index=True,
    )

    deployed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    service: Mapped["Service"] = relationship(
        back_populates="deployments",
    )