#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$POSTGRESQL_SERVER" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USERNAME"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing migrations"
alembic upgrade head

echo "Seeding admin user..."
python -m app.core.seed

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

