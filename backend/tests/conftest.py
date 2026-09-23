import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.db.model_registry  # noqa: F401
from app.core.config import settings
from app.core.roles import Roles
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.role import Role
from app.models.user import User


if not settings.test_database_url:
    raise RuntimeError(
        "TEST_DATABASE_URL must be configured "
        "before running tests."
    )


if "secureops_test" not in settings.test_database_url:
    raise RuntimeError(
        "Refusing to run tests against a non-test database."
    )


test_engine = create_engine(
    settings.test_database_url,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        expire_on_commit=False,
    )

    try:
        yield session

    finally:
        session.close()

        if transaction.is_active:
            transaction.rollback()

        connection.close()


@pytest.fixture
def client(
    db_session: Session,
):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[
        get_db
    ] = override_get_db

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

        token = response.json()[
            "access_token"
        ]

        return {
            "Authorization": (
                f"Bearer {token}"
            )
        }

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

