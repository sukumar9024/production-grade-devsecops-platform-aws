"""Observe SQL execution without logging query parameters or SQL text."""

from time import perf_counter

from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.metrics import DATABASE_QUERY_DURATION_SECONDS


def register_database_metrics(engine: Engine) -> None:
    @event.listens_for(engine, "before_cursor_execute")
    def before_execute(conn, cursor, statement, parameters, context, executemany):
        context.query_started_at = perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def after_execute(conn, cursor, statement, parameters, context, executemany):
        operation = (
            statement.lstrip().split(None, 1)[0].upper()
            if statement.strip()
            else "OTHER"
        )
        if operation not in {
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "ALTER",
            "DROP",
        }:
            operation = "OTHER"
        DATABASE_QUERY_DURATION_SECONDS.labels(operation=operation).observe(
            perf_counter() - context.query_started_at
        )
