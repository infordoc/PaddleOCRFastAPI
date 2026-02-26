# ============================================
# Multi-stage build for PaddleOCR 3.x FastAPI
# Optimized for Dokploy deployment
# ============================================

# Stage 1: Builder - Install dependencies
FROM python:3.9-slim-bullseye AS builder

WORKDIR /build

# Install system dependencies required for building Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libgl1 \
        libgomp1 \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Final lightweight image
FROM python:3.9-slim-bullseye

# Metadata
LABEL maintainer="PaddleOCR FastAPI" \
      description="PaddleOCR 3.x with FastAPI - Production Ready with VL Model Support" \
      version="3.x"

WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libgomp1 \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY main.py .
COPY log_conf.yaml .
COPY models ./models
COPY routers ./routers
COPY utils ./utils

# Create directory for model cache (both PaddleOCR and PaddleX models)
RUN mkdir -p /root/.paddleocr /root/.paddlex

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Run as non-root user for security (optional but recommended)
# Uncomment the following lines if you want to run as non-root
# RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /root/.paddleocr
# USER appuser

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
