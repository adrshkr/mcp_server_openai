# Minimal container to run the HTTP server
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only what we need to install & run
COPY pyproject.toml /app/
COPY src /app/src

# Install non-editable (cleaner in containers)
RUN pip install -U pip && pip install .

# Verify import at build time (fail early if broken)
RUN python - <<'PY'
import importlib
mod = importlib.import_module("mcp_server_openai.http_server")
assert getattr(mod, "app", None) is not None
print("HTTP app import OK")
PY

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "mcp_server_openai.http_server:app", "--host", "0.0.0.0", "--port", "8000"]