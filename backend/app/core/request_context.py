from contextvars import ContextVar

from fastapi import Request

request_id_context: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)


def set_request_id(
    request_id: str,
) -> None:
    request_id_context.set(request_id)


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
    # Uvicorn resolves proxy headers only from explicitly trusted proxy IPs.
    if request.client:
        return request.client.host

    return None


def get_route_template(request: Request) -> str:
    """Use the matched template, including FastAPI router prefixes, never raw URLs."""
    effective = request.scope.get("fastapi", {}).get("effective_route_context")
    if effective is not None:
        return effective.path
    route = request.scope.get("route")
    return route.path if route is not None else "unmatched"
