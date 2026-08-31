# The application implementation is expected to be added under ./app.
# This packaging deliberately keeps the runtime contract small:
# the service listens on PORT, stores state in /data, and writes episodes to /episodes.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ffmpeg curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt ./requirements.txt
RUN pip install --requirement requirements.txt

COPY app/ ./

RUN useradd --create-home --uid 10001 appuser \
    && mkdir --parents /data /episodes \
    && chown --recursive appuser:appuser /app /data /episodes

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl --fail --silent http://127.0.0.1:${PORT}/health || exit 1

CMD ["python", "-m", "app"]
