# Multi-stage Dockerfile for CloudNativePulse Application
# Stage 1: Build & Dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Minimal Distroless / Slim Production Image
FROM python:3.11-slim AS runner

WORKDIR /app

# Security: create non-root user
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -s /bin/bash -m appuser

# Copy installed python wheels from builder
COPY --from=builder /root/.local /home/appuser/.local

# Set environment paths
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    APP_NAME=CloudNativePulse \
    APP_VERSION=v1.0.0 \
    APP_ENV=production

# Copy application source code
COPY . /app/app

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Healthcheck for container runtime
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
