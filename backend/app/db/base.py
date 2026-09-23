from sqlalchemy.orm import DeclarativeBase
from app.db.base import Base

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
    RefreshToken,
)