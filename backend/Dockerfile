# Use official Python image as base
FROM python:3.13.2-slim AS builder

# Set the working directory inside the container
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    libpq-dev gcc

# Copy only requirements first for caching
COPY requirements.txt .

# Install dependencies in a virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# ========================
# Final Image (Smaller Size)
# ========================
FROM python:3.13.2-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Expose FastAPI's default port
EXPOSE 8000

# Ensure we are not running as root
RUN adduser --disabled-password --gecos '' fastapiuser && chown -R fastapiuser /app
USER fastapiuser

# Command to run FastAPI with Uvicorn (exec format for proper signal handling)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]