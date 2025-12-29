# Backend Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with increased timeout and retry
# SQLAlchemy and other large packages may take time to download
RUN pip install --no-cache-dir --default-timeout=300 --retries=5 -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic.ini .
COPY migrations/ ./migrations/
COPY app/scripts/start_backend.sh ./start_backend.sh

# Make startup script executable
RUN chmod +x /app/start_backend.sh

# Expose port
EXPOSE 8000

# Run the startup script
CMD ["/app/start_backend.sh"]

