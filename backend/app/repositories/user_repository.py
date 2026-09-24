import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository


class UserRepository:
    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:
        statement = select(User).where(User.email == email)

        return db.scalar(statement)

    @staticmethod
    def get_by_username(
        db: Session,
        username: str,
    ) -> User | None:
        statement = select(User).where(User.username == username)

        return db.scalar(statement)

    @staticmethod
    def get_by_email_or_username(
        db: Session,
        email: str,
        username: str,
    ) -> User | None:
        statement = select(User).where(
            or_(
                User.email == email,
                User.username == username,
            )
        )

        return db.scalar(statement)

    @staticmethod
    def create(
        db: Session,
        user: User,
    ) -> User:
        db.add(user)
        db.flush()
        AuditLogRepository.stage(
            db, "user.registered", "user", user.id, user_id=user.id
        )
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_by_login(
        db: Session,
        identity: str,
    ) -> User | None:
        normalized = identity.lower()

        statement = select(User).where(
            or_(
                User.email == normalized,
                User.username == normalized,
            )
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: uuid.UUID,
    ) -> User | None:
        statement = (
            select(User).options(joinedload(User.role)).where(User.id == user_id)
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[User]:
        statement = (
            select(User).options(joinedload(User.role)).order_by(User.created_at.desc())
        )

        return list(db.scalars(statement).unique().all())

    @staticmethod
    def save(
        db: Session,
        user: User,
    ) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)

        return user
