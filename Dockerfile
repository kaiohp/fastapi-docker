FROM python:3.12 as builder

ENV PIP_YES=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN pip install poetry==1.8.2 \
    && poetry install --only main --no-root \
    && rm -rf ${POETRY_CACHE_DIR} \
    && pip uninstall poetry

FROM python:3.12-slim as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /app

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src ./src
EXPOSE 8000
ENTRYPOINT [ "uvicorn", "src.main:app", "--host", "0.0.0.0" ]
