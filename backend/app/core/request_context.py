from fastapi import Request


def get_request_id(
    request: Request,
) -> str | None:
    return request.headers.get(
        "X-Request-ID"
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