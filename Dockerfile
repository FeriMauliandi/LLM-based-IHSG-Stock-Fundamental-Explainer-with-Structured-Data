# ===================================================
# Stage 1: Base Environment & Dependencies
# ===================================================
FROM python:3.12-slim-bookworm AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (curl for container health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create non-root system user for security
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Set appropriate permissions for non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser


# ===================================================
# Stage 2: FastAPI Backend + Web UI (/app)
# ===================================================
FROM base AS backend

# Expose port for FastAPI backend
EXPOSE 8000

# Health check probe against FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI server with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


# ===================================================
# Stage 3: Streamlit Interactive Dashboard
# ===================================================
FROM base AS streamlit

# Expose port for Streamlit
EXPOSE 8501

# Health check probe against Streamlit health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start Streamlit application
CMD ["streamlit", "run", "App.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]


# ===================================================
# Default Target: Backend (serves API & Web UI)
# ===================================================
FROM backend AS final