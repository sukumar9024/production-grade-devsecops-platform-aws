import pytest
from pydantic import ValidationError

from app.core.config import Settings


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
