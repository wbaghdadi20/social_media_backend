# Base Stage
FROM python:3.12.5 AS base

WORKDIR /usr/src/app

# Install curl to download wait-for-it.sh
RUN apt-get update && apt-get install -y curl

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download wait-for-it.sh script and make it executable
RUN curl -o /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Test Stage
FROM base AS test

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Set default environment variables for testing
ENV SQLALCHEMY_DATABASE_URL=postgresql://testuser:testpassword@test_postgres/test_db
ENV SECRET_KEY=test_secret_key
ENV ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30

# Set ENTRYPOINT to use wait-for-it.sh to wait for the test database
ENTRYPOINT ["/wait-for-it.sh", "test_postgres", "--"]

CMD ["pytest", "/usr/src/app/tests"]

# Production Stage
FROM base AS prod

# Set ENTRYPOINT to use wait-for-it.sh to wait for the database
ENTRYPOINT ["/wait-for-it.sh", "postgres", "--"]

# Set default command to start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]