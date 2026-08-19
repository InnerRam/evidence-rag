FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
RUN pip install --upgrade pip && pip install .

FROM base AS test

RUN pip install '.[dev]'
COPY tests ./tests
CMD ["python3", "-m", "pytest", "-q", "--cov=app", "--cov-fail-under=85"]

FROM base AS runtime

RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /data/uploads && chown -R app:app /app /data/uploads
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
