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
            db.execute(text("SELECT 1"))

            return DependencyHealth(status="healthy")

        except SQLAlchemyError:
            return DependencyHealth(
                status="unhealthy",
                detail="Database connection failed.",
            )

    @staticmethod
    def check_redis() -> DependencyHealth:
        from redis import Redis, RedisError

        from app.core.config import settings

        try:
            with Redis.from_url(
                settings.redis_url, socket_connect_timeout=2, socket_timeout=2
            ) as client:
                if not client.ping():
                    return DependencyHealth(
                        status="unhealthy", detail="Redis connection failed."
                    )
            return DependencyHealth(status="healthy")
        except (RedisError, ValueError):
            return DependencyHealth(
                status="unhealthy", detail="Redis connection failed."
            )
