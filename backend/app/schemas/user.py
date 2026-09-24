import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserStatus


class UserCreate(BaseModel):
    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )

    full_name: str | None = Field(
        default=None,
        max_length=255,
    )

    password: str = Field(
        min_length=12,
        max_length=128,
    )


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str | None

    status: UserStatus
    is_verified: bool

    role: RoleResponse

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserRoleUpdate(BaseModel):
    role: str


class UserStatusUpdate(BaseModel):
    status: UserStatus
