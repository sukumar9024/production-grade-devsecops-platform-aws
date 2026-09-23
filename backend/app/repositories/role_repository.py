from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role


class RoleRepository:
    @staticmethod
    def get_by_name(
        db: Session,
        name: str,
    ) -> Role | None:
        statement = select(Role).where(
            Role.name == name
        )

        return db.scalar(statement)