from contextvars import ContextVar

from fastapi import Request


request_id_context: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)


def set_request_id(
    request_id: str,
) -> None:
    request_id_context.set(
        request_id
    )


def get_current_request_id() -> str | None:
    return request_id_context.get()


def get_request_id(
    request: Request,
) -> str | None:
    return getattr(
        request.state,
        "request_id",
        None,
    )


def get_client_ip(
    request: Request,
) -> str | None:
    forwarded_for = request.headers.get(
        "X-Forwarded-For"
    )

    if forwarded_for:
        return (
            forwarded_for
            .split(",")[0]
            .strip()
        )

    if request.client:
        return request.client.host

    return None