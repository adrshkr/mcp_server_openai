# mcp_server_openai

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-compatible-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready FastMCP server implementation using the official MCP SDK. Provides mathematical operations, web content fetching, PowerPoint generation, and intelligent prompt management with client-specific configurations.

## ✨ Features

- **🔧 Tools**: Mathematical operations, web fetching, PowerPoint content generation
- **📊 Resources**: Health monitoring and system status
- **🎯 Prompts**: Jinja2-based templates with per-client customization
- **🚀 Dual Interface**: Both stdio and HTTP/SSE modes
- **📝 Structured Logging**: JSON-formatted request lifecycle tracking
- **🐳 Docker Ready**: Containerized deployment support

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Stdio Mode](#stdio-mode-with-mcp-dev-inspector)
  - [HTTP Mode](#http-mode-with-sse)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Docker](#-docker)
- [Development](#-development)
- [Project Structure](#-project-structure)
- [Changelog](#-changelog)

---

## 🚀 Quick Start

```bash
# Install with uv (recommended)
uv venv && uv sync

# Run in stdio mode with MCP inspector
uv run mcp dev src/mcp_server_openai/server.py:app

# Or run HTTP server
uv run uvicorn mcp_server_openai.http_server:app --host 0.0.0.0 --port 8000
```

---

## 📦 Requirements

- **Python 3.10+**
- **Node.js LTS** (for MCP Inspector; provides `npx`)
- **Optional**: Docker for containerized deployment
- **Recommended**: [`uv`](https://github.com/astral-sh/uv) for fast, reproducible environments

## 💾 Installation

### Using pip

```bash
python -m pip install -U pip
pip install -e .
```

### Using uv (Recommended)

```bash
uv venv
uv sync
```

---

## 🎮 Usage

### Stdio Mode with MCP Dev Inspector

```bash
# Install the CLI if needed
uv add "mcp[cli]"

# Start the inspector and spawn this server over stdio (path spec)
uv run mcp dev src/mcp_server_openai/server.py:app
```

#### Windows Setup Notes

Ensure `npx` is available on PATH:
- `C:\Program Files\nodejs\npx.cmd`, or  
- `%USERPROFILE%\AppData\Roaming\npm\npx.cmd`

#### Alternative Module Spec

After `pip install -e .`:
```bash
uv run mcp dev mcp_server_openai.server:app
```

### HTTP Mode with SSE

```bash
# Start HTTP server
uv run uvicorn mcp_server_openai.http_server:app --host 0.0.0.0 --port 8000

# Health checks
curl http://127.0.0.1:8000/health    # Returns: "ok"
curl http://127.0.0.1:8000/info      # Server information

# Server-Sent Events endpoint
curl -iN "http://127.0.0.1:8000/mcp/sse?client_id=local-test"
```

#### JavaScript SSE Example

```javascript
const es = new EventSource("http://127.0.0.1:8000/mcp/sse?client_id=local-test");
es.addEventListener("ready", (e) => console.log("ready", e.data));
es.onmessage = (e) => console.log("message", e.data);
es.onerror = (e) => console.error("sse error", e);
```

---

## 📖 API Reference

### 🔧 Tools

#### `math.add` / `math.sub`
Performs basic mathematical operations.

**Parameters:**
```json
{
  "a": 2,
  "b": 3
}
```

**Returns:** Numeric result

#### `web.fetch_url`
Fetches web content with comprehensive metadata.

**Parameters:**
```json
{
  "url": "https://example.com"
}
```

**Returns:**
```json
{
  "url": "https://example.com",
  "status_code": 200,
  "elapsed_ms": 245.3,
  "headers_json": "{\"content-type\": \"text/html\"}",
  "content_preview": "Web page content...",
  "truncated": false,
  "error": null
}
```

#### `content.create`
Generates PowerPoint presentations from structured data.

**Parameters:**
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

**Output:** Saves to `output/<Client>/<Project>/content.pptx`

### 📊 Resources

#### `health://ping`
Health check endpoint returning server status.

### 🎯 Prompts

#### `summarize`
Jinja2-based prompt with client-specific customization.

**Parameters:**
```json
{
  "topic": "Large Language Models",
  "tone": "concise",
  "client_id": "acme"
}
```

**Features:**
- File-based Jinja2 templates
- Per-client variable overrides
- Configurable via `MCP_CONFIG_PATH` (YAML) or `MCP_CONFIG_JSON`

---

## ⚙️ Configuration

### Per-Client Prompt Variables

Configure client-specific prompt behavior via YAML file or JSON environment variable.

#### YAML Configuration

Create `config.yaml`:
```yaml
prompts:
  summarize:
    defaults:
      tone: concise
    clients:
      acme:
        tone: detailed
        style: professional
```

#### Environment Variables

```bash
# YAML file path
export MCP_CONFIG_PATH=./config.yaml

# Or direct JSON
export MCP_CONFIG_JSON='{"prompts":{"summarize":{"defaults":{"tone":"concise"},"clients":{"acme":{"tone":"detailed"}}}}}'
```

#### Validation

Test your configuration:
```bash
uv run python -c "
from mcp_server_openai.config import get_prompt_vars
print('Default:', get_prompt_vars('summarize', client_id=None))
print('Acme client:', get_prompt_vars('summarize', client_id='acme'))
"
```

### CLI Tool Usage

Call tools directly from JSON files:

```bash
# Example: content creation
uv run python scripts/call_tool.py content.create params-content-create.json
```

#### Windows NPX Path Setup

If `npx` is not automatically detected:
```bash
# PowerShell (persistent)
setx NPX_PATH "C:\Program Files\nodejs\npx.cmd"

# Git Bash (session)
export NPX_PATH="/c/Program Files/nodejs/npx.cmd"
```

---

## 🧪 Testing

### Run Tests

```bash
# Using uv (recommended)
uv run python -m pytest -q

# Using pytest directly
pytest
```

### Platform-Specific Notes

**Windows SSE Tests**: Stream tests are skipped by default to avoid platform-specific blocking.

To force-run SSE tests on non-Windows:
```bash
unset SKIP_SSE_TESTS && uv run python -m pytest -q
```

### Coverage

```bash
uv run python -m pytest --cov=src/mcp_server_openai --cov-report=html
```

---

## 🐳 Docker

### Build and Run

```bash
# Build image
docker build -t mcp-server-openai:0.2.0 .

# Run container
docker run --rm -p 8000:8000 mcp-server-openai:0.2.0

# Health check
curl http://127.0.0.1:8000/health
curl -iN "http://127.0.0.1:8000/mcp/sse?client_id=local-test"
```

### Docker Compose

```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_CONFIG_JSON={"prompts":{"summarize":{"defaults":{"tone":"concise"}}}}
```

**Note**: Linux builds are case-sensitive. Ensure `README.md` filename matches exactly.

---

## 🛠️ Development

### Make Commands

```bash
make check      # Full check: preflight + tests + mypy
make preflight  # Code formatting and linting
make fmt        # Format code with Black
make lint       # Lint with Ruff
make test       # Run tests
make run-http   # Start HTTP server
```

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy .

# Full quality check
make check
```

---

## 📁 Project Structure

```
src/mcp_server_openai/
├── __main__.py              # CLI entrypoint
├── main.py                  # Main application logic
├── server.py                # FastMCP app factory + auto-discovery
├── http_server.py           # HTTP/SSE server (Starlette)
├── config.py                # YAML/JSON config loader
├── logging_utils.py         # Structured JSON logging
├── progress.py              # Progress tracking utilities
├── tools/
│   ├── __init__.py
│   ├── math_tools.py        # Mathematical operations
│   ├── web_tools.py         # Web content fetching
│   └── content_creator.py   # PowerPoint generation
├── resources/
│   ├── __init__.py
│   └── health.py            # Health check resources
└── prompts/
    ├── __init__.py
    ├── manager.py           # Jinja2 template manager
    ├── summarize.py         # Summarization prompts
    └── templates/
        └── summarize.j2     # Jinja2 template files

scripts/
├── call_tool.py             # CLI tool caller
├── cli.sh                   # Shell utilities
├── preflight.py             # Code quality checks
└── run.sh                   # Runtime scripts

tests/                       # Comprehensive test suite
├── conftest.py
├── test_*.py               # Unit tests for all modules
└── ...
```

---

## 📈 Changelog

### v0.2.0 - Current

**Milestone 2: Registry & Prompts**
- ✅ Auto-discovery of tools via `register(mcp)` pattern
- ✅ YAML/JSON config loader with per-client prompt variables  
- ✅ Jinja2-based prompt templates with client overrides
- ✅ Structured JSON logging with request lifecycle tracking

**Milestone 3.1: HTTP/SSE**
- ✅ Server-Sent Events streaming with keep-alive
- ✅ Health and info endpoints for monitoring
- ✅ Cross-platform compatibility (Windows-friendly tests)
- ✅ Docker containerization support

**Features:**
- 🔧 Mathematical operations (`math.add`, `math.sub`)
- 🌐 Web content fetching (`web.fetch_url`)
- 📄 PowerPoint generation (`content.create`)
- 🎯 Client-specific prompt customization
- 📊 Health monitoring resources

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes following the existing code style
4. Run quality checks: `make check`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

*Built with ❤️ using FastMCP and the Model Context Protocol*
