from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:
        statement = select(User).where(
            User.email == email
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_username(
        db: Session,
        username: str,
    ) -> User | None:
        statement = select(User).where(
            User.username == username
        )

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