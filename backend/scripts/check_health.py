import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal


def check_health() -> None:
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))

    except SQLAlchemyError as exc:
        print(f"Health check failed: {exc.__class__.__name__}")
        sys.exit(1)

    print("Health check passed.")


if __name__ == "__main__":
    check_health()
