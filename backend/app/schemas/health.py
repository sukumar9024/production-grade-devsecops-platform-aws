from typing import Literal

from pydantic import BaseModel


class LivenessResponse(BaseModel):
    status: Literal["alive"]


class DependencyHealth(BaseModel):
    status: Literal["healthy", "unhealthy"]
    detail: str | None = None


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    database: DependencyHealth
    redis: DependencyHealth
    request_id: str | None = None
