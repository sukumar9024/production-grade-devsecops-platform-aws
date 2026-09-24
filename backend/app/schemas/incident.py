import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    IncidentSeverity,
    IncidentStatus,
)


class IncidentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    service_id: uuid.UUID

    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str = Field(
        min_length=3,
        max_length=5000,
    )

    severity: IncidentSeverity


class IncidentUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        min_length=3,
        max_length=5000,
    )

    severity: IncidentSeverity | None = None

    status: IncidentStatus | None = None


class IncidentServiceResponse(BaseModel):
    id: uuid.UUID
    name: str
    environment: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class IncidentResponse(BaseModel):
    id: uuid.UUID

    title: str
    description: str

    severity: IncidentSeverity
    status: IncidentStatus

    detected_at: datetime
    resolved_at: datetime | None

    service: IncidentServiceResponse

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
