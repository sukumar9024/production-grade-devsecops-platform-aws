from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SecureOps API"
    app_version: str = "1.0.0"
    environment: str = "local"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    api_v1_prefix: str = "/api/v1"

    redis_url: str = "redis://localhost:6379/0"
    test_database_url: str | None = None
    database_url: str

    jwt_secret: str = Field(min_length=32, repr=False)
    jwt_algorithm: Literal["HS256"] = "HS256"

    access_token_expire_minutes: int = Field(default=15, ge=1, le=60)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)

    @field_validator("jwt_secret")
    @classmethod
    def reject_placeholder_secret(cls, value: str) -> str:
        if any(
            marker in value.lower()
            for marker in ("generate-me", "change-me", "changeme")
        ):
            raise ValueError("JWT_SECRET must be generated before startup")
        return value

    @model_validator(mode="after")
    def production_security(self):
        if self.environment in {"staging", "production"}:
            if self.debug:
                raise ValueError("Debug is forbidden in staging and production")
            if not urlsplit(self.redis_url).password:
                raise ValueError(
                    "Redis authentication is required in staging and production"
                )
            if "*" in self.cors_origins.split(","):
                raise ValueError("CORS must list explicit origins")
        return self

    model_config = SettingsConfigDict(
        hide_input_in_errors=True,
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
