from fastapi.exceptions import (
    RequestValidationError,
)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "request_id": get_request_id(
                request
            ),
        },
    )