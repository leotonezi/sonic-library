# ====================
# Base Image (Builder)
# ====================
FROM python:3.13.2-slim AS builder

WORKDIR /app

# Update and install build dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    python -m ensurepip && pip install --upgrade pip

# Copy only requirements for cache efficiency
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ========================
# Final Image (Runtime)
# ========================
FROM python:3.13.2-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python dependencies
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Create a non-root user
RUN adduser --disabled-password --gecos '' fastapiuser && chown -R fastapiuser /app
USER fastapiuser

# Start Uvicorn (use --reload only in development)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]