from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.health import DependencyHealth


class HealthService:
    @staticmethod
    def check_database(
        db: Session,
    ) -> DependencyHealth:
        try:
            db.execute(
                text("SELECT 1")
            )

            return DependencyHealth(
                status="healthy"
            )

        except SQLAlchemyError:
            return DependencyHealth(
                status="unhealthy",
                detail="Database connection failed.",
            )