# Multi-stage Docker build optimized for GCP Cloud Run
# Security: Non-root user, minimal attack surface, secure defaults
# Performance: Optimized layers, minimal image size, fast startup

# Stage 1: Build stage with full development environment
FROM python:3.11-slim-bullseye as builder

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Set up build directory
WORKDIR /build

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock* ./
COPY config/ ./config/

# Install dependencies in virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv sync --frozen

# Copy source code and startup script
COPY src/ ./src/
COPY scripts/startup.py ./scripts/

# Install the package
RUN uv pip install .

# Verify import at build time (fail early if broken)
RUN python - <<'PY'
import importlib
mod = importlib.import_module("mcp_server_openai.http_server")
assert getattr(mod, "app", None) is not None
print("HTTP app import OK")
PY

# Stage 2: Runtime stage with minimal footprint
FROM python:3.11-slim-bullseye as runtime

# Security: Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set up application directory
WORKDIR /app

# Copy application code with proper ownership
COPY --from=builder --chown=appuser:appuser /build/src ./src
COPY --from=builder --chown=appuser:appuser /build/config ./config
COPY --from=builder --chown=appuser:appuser /build/scripts/startup.py ./scripts/

# Create directories for data, logs, and scripts
RUN mkdir -p /app/data /app/logs /app/scripts \
    && chown -R appuser:appuser /app

# Security: Switch to non-root user
USER appuser

# Environment variables for production
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO
ENV PORT=8080

# GCP Cloud Run health checks - use comprehensive probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health/live || exit 1

# Expose port (Cloud Run uses PORT env var)
EXPOSE ${PORT}

# Startup command with pre-validation for optimal Cloud Run performance
CMD ["python", "scripts/startup.py"]
