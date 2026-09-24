import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        min_length=3,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class ProjectCreatorResponse(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None

    created_by: ProjectCreatorResponse

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
