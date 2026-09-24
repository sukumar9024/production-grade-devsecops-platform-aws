from collections.abc import Generator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.request_context import get_client_ip
from app.db.metrics import (
    register_database_metrics,
)

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 3},
)

register_database_metrics(engine)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db(request: Request) -> Generator[Session]:
    db = SessionLocal()
    db.info["client_ip"] = get_client_ip(request)

    try:
        yield db
    finally:
        db.close()
