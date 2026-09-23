import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.metrics import (
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)


class MetricsMiddleware(BaseHTTPMiddleware):
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

            status_code = response.status_code

        except Exception:
            status_code = 500

            self._record_metrics(
                request=request,
                status_code=status_code,
                start_time=start_time,
            )

            raise

        self._record_metrics(
            request=request,
            status_code=status_code,
            start_time=start_time,
        )

        return response

    @staticmethod
    def _record_metrics(
        request: Request,
        status_code: int,
        start_time: float,
    ) -> None:
        duration = (
            time.perf_counter()
            - start_time
        )

        route = request.scope.get("route")

        endpoint = (
            route.path
            if route is not None
            else "unmatched"
        )

        method = request.method
        status_code_label = str(
            status_code
        )

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code_label,
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        if status_code >= 400:
            HTTP_ERRORS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code_label,
            ).inc()