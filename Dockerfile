FROM python:3.12

RUN pip install poetry

WORKDIR /app

COPY . ./
RUN poetry install
EXPOSE 8000
ENTRYPOINT [ "poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload" ]