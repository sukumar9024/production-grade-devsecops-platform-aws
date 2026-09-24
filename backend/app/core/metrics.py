from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    [
        "method",
        "endpoint",
        "status_code",
    ],
)


HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    [
        "method",
        "endpoint",
    ],
)


HTTP_ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Total number of HTTP error responses",
    [
        "method",
        "endpoint",
        "status_code",
    ],
)


DATABASE_QUERY_DURATION_SECONDS = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    [
        "operation",
    ],
)


LOGIN_FAILURES_TOTAL = Counter(
    "login_failures_total",
    "Total number of failed login attempts",
)
