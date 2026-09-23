from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    @staticmethod
    def create(
        db: Session,
        token: RefreshToken,
    ) -> RefreshToken:
        db.add(token)
        db.commit()
        db.refresh(token)

        return token

    @staticmethod
    def get_by_jti(
        db: Session,
        jti: str,
    ) -> RefreshToken | None:
        statement = select(RefreshToken).where(
            RefreshToken.jti == jti
        )

        return db.scalar(statement)

    @staticmethod
    def revoke(
        db: Session,
        token: RefreshToken,
    ) -> None:
        token.revoked = True
        token.revoked_at = datetime.now(UTC)

        db.add(token)
        db.commit()