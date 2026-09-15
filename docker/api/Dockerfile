FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

COPY apps/api/pyproject.toml ./
RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt] bcrypt pandas numpy scikit-learn networkx aiofiles python-multipart structlog redis celery

COPY apps/api /app
COPY ml /ml

ENV PYTHONPATH=/app:/ml

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
