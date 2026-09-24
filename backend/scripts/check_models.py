import app.db.model_registry  # noqa: F401
from app.db.base import Base


def main() -> None:
    print("Registered database tables:")

    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"- {table_name}")


if __name__ == "__main__":
    main()
