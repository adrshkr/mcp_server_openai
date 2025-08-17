.PHONY: all check preflight fmt lint test clean run docker-build docker-run compose-up compose-down

all: check

check:
	@echo "--- Full check: preflight + tests + mypy ---"
	@$(MAKE) -s preflight
	@uv run pytest
	@uv run mypy src/mcp_server_openai

preflight:
	@echo "--- Running preflight checks (Black -> Ruff) ---"
	@uv run python scripts/preflight.py

fmt:
	@echo "--- Formatting with Black ---"
	@uv run black .

lint:
	@echo "--- Linting with Ruff ---"
	@uv run ruff check .

test:
	@echo "--- Running tests with pytest ---"
	@uv run pytest

clean:
	@echo "--- Cleaning up ---"
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@rm -rf .pytest_cache .mypy_cache .coverage build dist .venv

run:
	@uv run mcp_server_openai --name "from Makefile"

docker-build:
	@docker build -t mcp_server_openai:dev .

docker-run: docker-build
	@docker run --rm --env-file local.env mcp_server_openai:dev

compose-up:
	@docker compose up --build -d

compose-down:
	@docker compose down -v
