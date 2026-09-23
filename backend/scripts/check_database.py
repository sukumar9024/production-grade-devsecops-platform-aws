from sqlalchemy import text

from app.db.session import engine


def check_database_connection() -> None:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1")
        )

        value = result.scalar_one()

        if value != 1:
            raise RuntimeError("Database connectivity check failed")

        print("Database connection successful.")


if __name__ == "__main__":
    check_database_connection()