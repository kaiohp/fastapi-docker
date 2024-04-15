FROM python:3.12

RUN pip install poetry==1.8.2

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY src ./src
RUN poetry install --only main
EXPOSE 8000
ENTRYPOINT [ "poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload" ]
