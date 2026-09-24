"""PostgreSQL integration fixtures: isolated schema, rolled-back transactions."""

import os
import uuid

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.request_context import get_client_ip

# Never load application credentials for tests. Only TEST_DATABASE_URL is used.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://invalid@127.0.0.1:1/unused"
)
os.environ["JWT_SECRET"] = "unit-test-only-secret-" + "x" * 32
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "false"

import app.db.model_registry
from app.core.roles import Roles
from app.core.security import hash_password
from app.db.base import Base
from app.db.metrics import register_database_metrics
from app.db.session import get_db
from app.main import app
from app.models.role import Role
from app.models.user import User


@pytest.fixture(scope="session")
def test_engine():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.fail(
            "Set TEST_DATABASE_URL to a PostgreSQL database; tests create an isolated schema."
        )
    schema = "test_" + uuid.uuid4().hex
    admin_engine = create_engine(url)
    with admin_engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(
        url, connect_args={"options": f"-csearch_path={schema}"}, pool_pre_ping=True
    )
    register_database_metrics(engine)
    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin_engine.dispose()


@pytest.fixture
def db_session(test_engine):
    with test_engine.connect() as connection:
        transaction = connection.begin()
        session = Session(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def client(
    db_session: Session,
):
    def override_get_db(request: Request):
        db_session.info.clear()
        db_session.info["client_ip"] = get_client_ip(request)
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def roles(
    db_session: Session,
):
    admin_role = Role(
        name=Roles.ADMIN,
        description="Administrator",
    )

    engineer_role = Role(
        name=Roles.ENGINEER,
        description="Engineer",
    )

    viewer_role = Role(
        name=Roles.VIEWER,
        description="Viewer",
    )

    db_session.add_all(
        [
            admin_role,
            engineer_role,
            viewer_role,
        ]
    )

    db_session.flush()

    return {
        Roles.ADMIN: admin_role,
        Roles.ENGINEER: engineer_role,
        Roles.VIEWER: viewer_role,
    }


@pytest.fixture
def auth_headers(
    client,
):
    def login(
        identity: str,
        password: str,
    ):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "identity": identity,
                "password": password,
            },
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        return {"Authorization": (f"Bearer {token}")}

    return login


@pytest.fixture
def admin_user(
    user_factory,
):
    return user_factory(
        role=Roles.ADMIN,
        username="admin_test",
        email="admin_test@example.com",
    )


@pytest.fixture
def engineer_user(
    user_factory,
):
    return user_factory(
        role=Roles.ENGINEER,
        username="engineer_test",
        email="engineer_test@example.com",
    )


@pytest.fixture
def viewer_user(
    user_factory,
):
    return user_factory(
        role=Roles.VIEWER,
        username="viewer_test",
        email="viewer_test@example.com",
    )


@pytest.fixture
def user_factory(db_session, roles):
    def create_user(
        role=Roles.VIEWER,
        username=None,
        email=None,
        password="SecurePassword123!",
        **kwargs,
    ):
        suffix = uuid.uuid4().hex[:12]
        user = User(
            username=username or f"user_{suffix}",
            email=email or f"{suffix}@example.com",
            password_hash=hash_password(password),
            role=roles[role],
            **kwargs,
        )
        db_session.add(user)
        db_session.flush()
        return user

    return create_user


@pytest.fixture
def project(db_session, admin_user):
    from app.models.project import Project

    item = Project(name="Fixture project", created_by_id=admin_user.id)
    db_session.add(item)
    db_session.flush()
    return item


@pytest.fixture
def service(db_session, project):
    from app.models.enums import Environment
    from app.models.service import Service

    item = Service(
        name="Fixture service", project_id=project.id, environment=Environment.DEV
    )
    db_session.add(item)
    db_session.flush()
    return item
