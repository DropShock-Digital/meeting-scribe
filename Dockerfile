FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN useradd --create-home --uid 10001 app && mkdir /data && chown app:app /data
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /usr/local/bin/
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

USER app
ENV PATH="/opt/venv/bin:$PATH" \
    MEETING_SCRIBE_DATA_DIR=/data \
    MEETING_SCRIBE_BIND_HOST=0.0.0.0 \
    MEETING_SCRIBE_PORT=8080
VOLUME ["/data"]
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8080/api/health', timeout=3)"
CMD ["meeting-scribe", "serve"]
