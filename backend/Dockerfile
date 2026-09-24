FROM python:3.14.7-alpine3.23@sha256:218761489de417a6eb0808e264cbdd7043ec6659fe5a61898815e9848536541d AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --only-binary=:all: -r requirements.txt \
    && /opt/venv/bin/python -m pip uninstall -y pip

FROM python:3.14.7-alpine3.23@sha256:218761489de417a6eb0808e264cbdd7043ec6659fe5a61898815e9848536541d AS runtime
RUN apk upgrade --no-cache \
    && python -m pip uninstall -y pip \
    && rm -rf /usr/local/lib/python3.14/ensurepip \
    && addgroup -g 10001 appuser \
    && adduser -D -H -u 10001 -G appuser appuser
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser migrations ./migrations
COPY --chown=appuser:appuser scripts ./scripts
COPY --chown=appuser:appuser alembic.ini ./alembic.ini
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=3)"
# One worker keeps Prometheus counters coherent; scale with container replicas.
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--worker-class", "uvicorn_worker.UvicornWorker", "--worker-tmp-dir", "/tmp", "--access-logfile", "-", "--error-logfile", "-", "--timeout", "60", "--graceful-timeout", "30"]
