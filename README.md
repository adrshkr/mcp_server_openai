# mcp\_server\_openai

A minimal, production-ready-ish FastMCP server (Python) using the official MCP SDK.

Exposes:

* Tools: `math.add`, `math.sub`, `web.fetch_url`, `content.create` (PPT-first)
* Resource: `health://ping`
* Prompt: `summarize(topic, tone="concise", client_id=None)` with per-client overrides

---

## Requirements

* Python 3.10+
* Node.js LTS (for the MCP Inspector; provides `npx`)
* Optional: Docker
* Optional: [`uv`](https://github.com/astral-sh/uv) for fast, reproducible envs

## Install

```bash
python -m pip install -U pip
pip install -e .
```

Or with uv:

```bash
uv venv
uv sync
```

---

## Run (stdio) with MCP dev inspector

```bash
# Install the CLI if needed
uv add "mcp[cli]"

# Start the inspector and spawn this server over stdio (path spec)
uv run mcp dev src/mcp_server_openai/server.py:app
```

Notes:

* Requires `npx` on PATH. On Windows, ensure either:

  * `C:\\Program Files\\nodejs\\npx.cmd`, or
  * `%USERPROFILE%\\AppData\\Roaming\\npm\\npx.cmd`
* Prefer the path spec above. If you want a module spec, first `pip install -e .` then:

  ```bash
  uv run mcp dev mcp_server_openai.server:app
  ```

---

## Run (HTTP, SSE is live)

```bash
uv run uvicorn mcp_server_openai.http_server:app --host 0.0.0.0 --port 8000

# Health and info
curl http://127.0.0.1:8000/health    # -> ok
curl http://127.0.0.1:8000/info

# SSE (live)
curl -iN "http://127.0.0.1:8000/mcp/sse?client_id=local-test"
# -> 200 OK, Content-Type: text/event-stream
#    : connected ...
#    event: ready
#    data: {}
#    : keep-alive
```

Tiny JS example:

```js
const es = new EventSource("http://127.0.0.1:8000/mcp/sse?client_id=local-test");
es.addEventListener("ready", (e) => console.log("ready", e.data));
es.onmessage = (e) => console.log("message", e.data);
es.onerror = (e) => console.error("sse error", e);
```

---

## Tools

### math.add / math.sub

```json
{ "a": 2, "b": 3 }
```

### web.fetch\_url

Returns a flat JSON result suitable for the Inspector.

```json
{ "url": "https://example.com" }
```

Output fields include: `url`, `status_code`, `elapsed_ms`, `headers_json`, `content_preview`, `truncated`, `error`.

### content.create (PPT-first)

Creates a PPTX from a brief and source highlights; saves under `output/<Client>/<Project>/content.pptx`.

Example payload:

```json
{
  "client_name": "Acme",
  "project_name": "Q3",
  "source_content_type": "Highlight",
  "source_content_details": [
    "Market share +3%",
    "Beta launched",
    "4 enterprise wins"
  ],
  "target_content_type": "PPT",
  "number_of_slides": 5,
  "content_brief": "Client-facing deck focusing on achievements and next steps."
}
```

---

## Prompt: summarize

Optional `client_id` selects per-client defaults (see Config).

```json
{ "topic": "LLMs", "client_id": "acme" }
```
Note: Prompts are file-based (Jinja2) and can merge per-client variables from MCP_CONFIG_JSON or MCP_CONFIG_PATH (YAML). See config.example.yaml.

---

## Config (per-client prompt vars)

Provide defaults and per-client overrides via **YAML file** or **JSON env var**.

Example YAML (`config.yaml`):

```yaml
prompts:
  summarize:
    defaults:
      tone: concise
    clients:
      acme:
        tone: detailed
```

Run with:

```bash
# choose one
export MCP_CONFIG_PATH=./config.yaml
# or
export MCP_CONFIG_JSON='{"prompts":{"summarize":{"defaults":{"tone":"concise"},"clients":{"acme":{"tone":"detailed"}}}}}'
```

Quick sanity check:

```bash
uv run python - <<'PY'
from mcp_server_openai.config import get_prompt_vars
print("no client:", get_prompt_vars("summarize", client_id=None))
print("acme:", get_prompt_vars("summarize", client_id="acme"))
PY
```

---

## Call tools from JSON (no browser)

Use the helper script:

```bash
# content.create example
uv run python scripts/call_tool.py content.create params-content-create.json
```

If `npx` is not detected automatically on Windows, set:

```bash
# PowerShell (persist)
setx NPX_PATH "C:\\Program Files\\nodejs\\npx.cmd"
# Git Bash (session)
export NPX_PATH="/c/Program Files/nodejs/npx.cmd"
```

---

## Tests

```bash
uv run python -m pytest -q
# or
pytest
```

SSE test note on Windows: the SSE stream smoke test is skipped by default to avoid platform-specific blocking. To force-run on non-Windows, unset `SKIP_SSE_TESTS`.

```bash
# bash
unset SKIP_SSE_TESTS && uv run python -m pytest -q
```

---

## Docker

```bash
# build (adjust tag as needed)
docker build -t mcp-server-openai:0.2.3 .

# run
docker run --rm -p 8000:8000 mcp-server-openai:0.2.3

# verify
curl http://127.0.0.1:8000/health
curl -iN "http://127.0.0.1:8000/mcp/sse?client_id=local-test"
```

Tip (Windows): Docker builds on Linux are case-sensitive. Ensure the file is `README.md` or update the Dockerfile to copy `README.md` exactly.

---

## Makefile helpers (optional)

```make
check:  ## preflight + tests + mypy
	@echo "--- Full check: preflight + tests + mypy ---"; \
	make preflight && make test && uv run mypy .

preflight:
	@echo "--- Running preflight checks (Black -> Ruff) ---"; \
	uv run black --diff --check . || true; \
	uv run black .; \
	uv run ruff check .

fmt:
	uv run black .

lint:
	uv run ruff check .

test:
	uv run python -m pytest -q

run-http:
	uv run uvicorn mcp_server_openai.http_server:app --host 0.0.0.0 --port $${PORT-8000}
```

---

## Project layout

```
src/mcp_server_openai/
  server.py                # FastMCP app factory + auto-discovery
  http_server.py           # HTTP app (health/info; SSE live)
  config.py                # YAML/ENV config loader for prompt vars
  tools/
    __init__.py
    math_tools.py
    web_tools.py
    content_creator.py     # PPT-first content generation
  resources/
    health.py
  prompts/
    summarize.py
scripts/
  call_tool.py             # CLI helper to call tools from a JSON file
tests/
  test_math_tools.py
  test_web_tools.py
  test_resources.py
  test_prompts.py
  test_config.py
  test_content_creator.py
  test_http_server.py
```

---

## Changelog (high level)

* Milestone 2: Registry & Prompts

  * Auto-discovery of tools via `register(mcp)` in `mcp_server_openai.tools.*`.
  * Config loader (`MCP_CONFIG_PATH` YAML or `MCP_CONFIG_JSON` env) with per-client prompt vars.
  * `summarize` prompt reads merged defaults and client-specific overrides.
* Milestone 3.1: HTTP/SSE

  * `/mcp/sse` streams: initial `ready` event + periodic keep-alives.
  * Health/info endpoints exposed for readiness probes.
  * Windows-friendly tests (SSE smoke test skipped by default).
