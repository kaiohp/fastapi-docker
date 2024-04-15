FROM python:3.12-buster

RUN pip install poetry==1.8.2

ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main && rm -rf ${POETRY_CACHE_DIR}

COPY src ./src
EXPOSE 8000
ENTRYPOINT [ "poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0" ]
