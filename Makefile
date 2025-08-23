.PHONY: all check check-all preflight fmt lint test test-fast test-all clean run docker-build docker-run compose-up compose-down mypy-check mypy-full mypy-core

# Pytest configuration for fast vs full runs
PYTEST := uv run pytest
# Fast mode: skip non-critical markers if present, fail fast, show slow tests
PYTEST_FLAGS_FAST := -q --maxfail=1 --durations=10 -m "not slow and not integration and not e2e and not network"
# Full mode: run everything but still show durations for visibility
PYTEST_FLAGS_ALL := -q --durations=10
# Default test target path (can be overridden: make test TEST_ARGS=path)
TEST_ARGS ?= tests

all: check

check:
	@echo "--- Fast check: preflight + fast tests + mypy (core) ---"
	@$(MAKE) -s preflight
	@$(MAKE) -s test-fast
	@$(MAKE) -s mypy-check

check-all:
	@echo "--- Full check: preflight + ALL tests + mypy (full) ---"
	@$(MAKE) -s preflight
	@$(MAKE) -s test-all
	@$(MAKE) -s mypy-full

mypy-check:
	@echo "--- Running MyPy type checking (core files) ---"
	@$(MAKE) -s mypy-core

mypy-full:
	@echo "--- Running full MyPy type checking (may be slow) ---"
	@uv run mypy --config-file config/mypy.ini src/mcp_server_openai

mypy-core:
	@echo "--- Running MyPy on core files only ---"
	@uv run mypy --config-file config/mypy.ini src/mcp_server_openai/__init__.py src/mcp_server_openai/__main__.py src/mcp_server_openai/server.py src/mcp_server_openai/health.py src/mcp_server_openai/security.py src/mcp_server_openai/api/http_server.py

preflight:
	@echo "--- Running preflight checks (Black -> Ruff) ---"
	@uv run python scripts/utilities/preflight.py

fmt:
	@echo "--- Formatting with Black ---"
	@uv run black .

lint:
	@echo "--- Linting with Ruff ---"
	@uv run ruff check .

test: test-fast

test-fast:
	@echo "--- Running FAST tests (markers excluded: slow, integration, e2e, network) ---"
	@$(PYTEST) $(PYTEST_FLAGS_FAST) $(TEST_ARGS)

test-all:
	@echo "--- Running ALL tests ---"
	@$(PYTEST) $(PYTEST_FLAGS_ALL) $(TEST_ARGS)

clean:
	@echo "--- Cleaning up ---"
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@rm -rf .pytest_cache .mypy_cache .coverage build dist .venv

run:
	@uv run mcp_server_openai --name "from Makefile"

run-http:
	@echo "--- Starting enhanced HTTP server ---"
	@uv run uvicorn mcp_server_openai.api.streaming_http:app --host 0.0.0.0 --port 8000 --reload

run-enhanced:
	@echo "--- Starting enhanced HTTP server with optimizations ---"
	@uv run python -m mcp_server_openai.enhanced_server --host 0.0.0.0 --port 8000 --reload

run-prod:
	@echo "--- Starting production HTTP server ---"
	@uv run python -m mcp_server_openai.enhanced_server --host 0.0.0.0 --port 8000 --workers 4

docker-build:
	@docker build -t mcp_server_openai:dev .

docker-run: docker-build
	@docker run --rm --env-file local.env mcp_server_openai:dev

compose-up:
	@docker compose up --build -d

compose-down:
	@docker compose down -v
