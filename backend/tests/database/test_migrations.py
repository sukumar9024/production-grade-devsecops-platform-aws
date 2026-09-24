import os
import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.db.base import Base


def test_upgrade_downgrade_upgrade_in_isolated_schema(monkeypatch):
    url = os.environ["TEST_DATABASE_URL"]
    schema = "migration_" + uuid.uuid4().hex
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    scoped_url = (
        url + ("&" if "?" in url else "?") + f"options=-csearch_path%3D{schema}"
    )
    from app.core.config import settings

    monkeypatch.setattr(settings, "database_url", scoped_url)
    backend = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend / "migrations"))
    scoped = create_engine(scoped_url)
    try:
        command.upgrade(cfg, "head")
        assert set(Base.metadata.tables) <= set(inspect(scoped).get_table_names())
        command.check(cfg)
        command.downgrade(cfg, "base")
        assert inspect(scoped).get_table_names() == ["alembic_version"]
        command.upgrade(cfg, "head")
        assert "refresh_tokens" in inspect(scoped).get_table_names()
    finally:
        scoped.dispose()
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()
