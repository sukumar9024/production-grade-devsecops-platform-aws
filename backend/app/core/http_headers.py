from app.core.request_context import (
    get_current_request_id,
)


def build_downstream_headers() -> dict[str, str]:
    headers: dict[str, str] = {}

    request_id = (
        get_current_request_id()
    )

    if request_id is not None:
        headers[
            "X-Request-ID"
        ] = request_id

    return headers