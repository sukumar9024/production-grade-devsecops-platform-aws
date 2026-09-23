import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.request_context import (
    set_request_id,
)


REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        incoming_request_id = (
            request.headers.get(
                REQUEST_ID_HEADER
            )
        )

        incoming_request_id = (
            request.headers.get(
                REQUEST_ID_HEADER
            )
        )

        if (
            incoming_request_id
            and 1 <= len(
                incoming_request_id.strip()
            ) <= 100
        ):
            request_id = (
                incoming_request_id.strip()
            )
        else:
            request_id = str(
                uuid.uuid4()
            )

        request.state.request_id = (
            request_id
        )

        set_request_id(
            request_id
        )

        response = await call_next(
            request
        )

        response.headers[
            REQUEST_ID_HEADER
        ] = request_id

        return response