# Stage 1: Build and Test Stage
FROM python:3.12.5 AS builder

WORKDIR /usr/src/app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy the application code
COPY . .

# Run tests
RUN pytest /usr/src/app/tests

# Stage 2: Production Image
FROM python:3.12.5

WORKDIR /usr/src/app

# Copy only necessary files from the builder stage
COPY requirements.txt ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --from=builder /usr/src/app/app ./app

# Set the command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]