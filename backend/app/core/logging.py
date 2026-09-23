import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings


RESERVED_LOG_RECORD_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.now(
                UTC
            ).isoformat(),
            "level": record.levelname,
            "service": "backend",
            "environment": settings.environment,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if (
                key not in RESERVED_LOG_RECORD_FIELDS
                and key not in log_record
            ):
                log_record[key] = value

        if record.exc_info:
            log_record["exception"] = (
                self.formatException(
                    record.exc_info
                )
            )

        return json.dumps(
            log_record,
            default=str,
        )
    def configure_logging() -> None:
    handler = logging.StreamHandler()

    handler.setFormatter(
        JsonFormatter()
    )

    root_logger = logging.getLogger()

    root_logger.handlers.clear()

    root_logger.addHandler(
        handler
    )

    root_logger.setLevel(
        settings.log_level.upper()
    )