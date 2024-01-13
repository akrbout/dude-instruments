FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
COPY . /app

CMD ["uvicorn", "src.main:app", "--port", "5346"]