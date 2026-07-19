FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-cache --no-root

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]