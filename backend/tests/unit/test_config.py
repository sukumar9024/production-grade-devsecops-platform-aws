import hashlib

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_retired_jwt_secret_rejected_without_exposing_value(monkeypatch):
    # Exercise revocation without recommitting the real historical credential.
    secret = "synthetic-retired-test-value-" + "x" * 32
    monkeypatch.setattr(
        "app.core.config.RETIRED_JWT_SECRET_HASHES",
        frozenset({hashlib.sha256(secret.encode()).hexdigest()}),
    )
    with pytest.raises(ValidationError, match="was exposed") as error:
        Settings(_env_file=None, jwt_secret=secret)
    assert secret not in str(error.value)


def test_jwt_placeholder_rejected():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None, jwt_secret="generate-me-before-starting-the-application"
        )


def test_weak_jwt_secret_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret="short")


def test_unsafe_jwt_algorithm_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_algorithm="none")


def test_production_debug_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="production", debug=True)


def test_production_requires_redis_authentication():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None, environment="production", redis_url="rediss://redis:6379/0"
        )
