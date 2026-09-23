from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import (  # noqa: E402, F401
    AuditLog,
    Deployment,
    Incident,
    Project,
    Role,
    Service,
    User,
)