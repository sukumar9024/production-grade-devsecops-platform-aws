import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.request_context import get_request_id

logger = logging.getLogger(__name__)


def error_response(
    request: Request, status_code: int, detail, headers=None
) -> JSONResponse:
    request_id = get_request_id(request)
    response_headers = dict(headers or {})
    if request_id:
        response_headers["X-Request-ID"] = request_id
    return JSONResponse(
        status_code=status_code,
        headers=response_headers,
        content={"detail": detail, "request_id": request_id},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return error_response(request, exc.status_code, exc.detail, exc.headers)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Validation input can include passwords or bearer tokens; never reflect it.
    errors = [
        {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return error_response(request, 422, errors)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Exception text (e.g. SQL parameters) can contain credentials.
    logger.error(
        "Unhandled request error",
        extra={"error_type": type(exc).__name__, "request_id": get_request_id(request)},
    )
    return error_response(request, 500, "Internal server error.")
