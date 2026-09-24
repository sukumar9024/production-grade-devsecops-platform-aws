"""Import every mapped class for Alembic and standalone database scripts."""

from app.models import (  # noqa: F401
    AuditLog,
    Deployment,
    Incident,
    Project,
    RefreshToken,
    Role,
    Service,
    User,
)
