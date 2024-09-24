# Base Stage
FROM python:3.12.5 AS base

WORKDIR /usr/src/app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Test Stage
FROM base AS test

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Set default environment variables for testing
ENV SQLALCHEMY_DATABASE_URL=postgresql://testuser:testpassword@test_postgres/test_db
ENV SECRET_KEY=test_secret_key
ENV ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30

CMD ["pytest", "/usr/src/app/tests"]

# Production Stage
FROM base AS prod

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]