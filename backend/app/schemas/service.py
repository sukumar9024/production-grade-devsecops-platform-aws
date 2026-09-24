import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.enums import Environment, ServiceStatus


class ServiceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    project_id: uuid.UUID

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    environment: Environment

    version: str | None = Field(
        default=None,
        max_length=100,
    )

    health_check_url: HttpUrl | None = None


class ServiceUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    environment: Environment | None = None

    version: str | None = Field(
        default=None,
        max_length=100,
    )

    status: ServiceStatus | None = None

    health_check_url: HttpUrl | None = None


class ServiceProjectResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class ServiceResponse(BaseModel):
    id: uuid.UUID

    name: str
    environment: Environment
    version: str | None
    status: ServiceStatus
    health_check_url: str | None

    project: ServiceProjectResponse

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
