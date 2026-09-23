import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class AuditLogResponse(BaseModel):
    id: uuid.UUID

    action: str
    resource_type: str
    resource_id: str | None

    request_id: str | None
    ip_address: str | None

    details: dict[str, Any] | None

    user: AuditUserResponse | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
    