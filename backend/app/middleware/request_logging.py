import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


logger = logging.getLogger(
    "secureops.http"
)


class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        start_time = time.perf_counter()

        try:
            response = await call_next(
                request
            )

        except Exception:
            duration_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            self._log_request(
                request=request,
                status_code=500,
                duration_ms=duration_ms,
                level=logging.ERROR,
            )

            raise

        duration_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        level = (
            logging.ERROR
            if response.status_code >= 500
            else logging.WARNING
            if response.status_code >= 400
            else logging.INFO
        )

        self._log_request(
            request=request,
            status_code=response.status_code,
            duration_ms=duration_ms,
            level=level,
        )

        return response

    @staticmethod
    def _log_request(
        request: Request,
        status_code: int,
        duration_ms: float,
        level: int,
    ) -> None:
        route = request.scope.get(
            "route"
        )

        endpoint = (
            route.path
            if route is not None
            else "unmatched"
        )

        logger.log(
            level,
            "HTTP request completed",
            extra={
                "method": request.method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration_ms": round(
                    duration_ms,
                    2,
                ),
            },
        )