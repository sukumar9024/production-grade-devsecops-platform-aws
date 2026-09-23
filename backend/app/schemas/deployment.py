import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DeploymentStatus


class DeploymentCreate(BaseModel):
    service_id: uuid.UUID

    version: str = Field(
        min_length=1,
        max_length=100,
    )

    git_commit: str = Field(
        min_length=7,
        max_length=64,
    )

    image_digest: str | None = Field(
        default=None,
        max_length=255,
    )

    pipeline_id: str | None = Field(
        default=None,
        max_length=100,
    )


class DeploymentUpdate(BaseModel):
    status: DeploymentStatus | None = None

    image_digest: str | None = Field(
        default=None,
        max_length=255,
    )

    pipeline_id: str | None = Field(
        default=None,
        max_length=100,
    )

    deployed_at: datetime | None = None

    failure_reason: str | None = Field(
        default=None,
        max_length=5000,
    )


class DeploymentServiceResponse(BaseModel):
    id: uuid.UUID
    name: str
    environment: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class DeploymentResponse(BaseModel):
    id: uuid.UUID

    version: str
    git_commit: str
    image_digest: str | None
    pipeline_id: str | None

    status: DeploymentStatus

    deployed_at: datetime | None
    failure_reason: str | None

    service: DeploymentServiceResponse

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )