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
- **📈 Progress Tracking**: Real-time progress monitoring with ETA calculation and hierarchical support
- **💰 Usage Monitoring**: Comprehensive Claude API cost tracking and rate limiting
- **🔄 Real-time Streaming**: Enhanced SSE/WebSocket with live usage updates
- **🐳 Docker Ready**: Containerized deployment support

---

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📦 Requirements](#-requirements)
- [💾 Installation](#-installation)
- [🎮 Usage](#-usage)
- [📖 API Reference](#-api-reference)
- [📈 Progress Tracking](#-progress-tracking)
- [⚙️ Configuration](#️-configuration)
- [🧪 Testing](#-testing)
- [🐳 Docker](#-docker)
- [🛠️ Development](#️-development)
- [📁 Project Structure](#-project-structure)
- [📈 Changelog](#-changelog)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🚀 Quick Start

1.  **Install Dependencies:**

    ```bash
    # Install with uv (recommended)
    uv venv && uv sync
    ```

2.  **Run the Server:**

    *   **Stdio Mode (for development):**

        ```bash
        uv run mcp dev src/mcp_server_openai/server.py:app
        ```

    *   **HTTP Mode (for production):**

        ```bash
        uv run uvicorn mcp_server_openai.streaming_http:app --host 0.0.0.0 --port 8000
        ```

---

## 📦 Requirements

- **Python 3.10+**
- **Node.js LTS** (for MCP Inspector; provides `npx`)
- **Optional**: Docker for containerized deployment
- **Recommended**: [`uv`](https://github.com/astral-sh/uv) for fast, reproducible environments

---

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

The stdio mode is ideal for development and debugging.

```bash
# Install the MCP CLI if you haven't already
uv add "mcp[cli]"

# Start the inspector and spawn the server over stdio
uv run mcp dev src/mcp_server_openai/server.py:app
```

#### Windows Setup

Ensure `npx` is available on your `PATH`. Common locations include:
- `C:\Program Files\nodejs\npx.cmd`
- `%USERPROFILE%\AppData\Roaming\npm\npx.cmd`

### HTTP Mode with Modern Streaming

The HTTP mode provides a robust, production-ready server with advanced features.

```bash
# Start the modern HTTP server
uv run uvicorn mcp_server_openai.streaming_http:app --host 0.0.0.0 --port 8000

# Or use the enhanced server runner for graceful shutdown
uv run python -m mcp_server_openai.enhanced_server --host 0.0.0.0 --port 8000
```

You can interact with the server using `curl` or any HTTP client.

---

## 📖 API Reference

### 🔧 Tools

#### `math.add` / `math.sub`

Performs basic mathematical operations.

- **Parameters:** `{"a": <number>, "b": <number>}`
- **Returns:** The result of the operation.

#### `web.fetch_url`

Fetches web content and returns a comprehensive set of metadata.

- **Parameters:** `{"url": "<string>"}`
- **Returns:** A JSON object with the URL, status code, headers, and content preview.

#### `content.create`

Generates a PowerPoint presentation from structured data.

- **Parameters:** A JSON object with details about the presentation.
- **Output:** A `.pptx` file saved to the `output/<Client>/<Project>/` directory.

### 📊 Resources

#### `health://ping`

A health check endpoint that returns the server's status.

### 🎯 Prompts

The server includes an enhanced prompt management system with advanced template capabilities.

#### Available Prompts

- **`summarize`**: An advanced summarization prompt with client-specific customization.
- **`content_create`**: A template-based content creation system with rich customization.

---

## 📈 Progress Tracking

The server includes a modern progress tracking system that provides real-time monitoring, percentage tracking, ETA calculation, and hierarchical progress support.

--- 

## ⚙️ Configuration

### Per-Client Prompt Variables

You can configure client-specific prompt behavior using either a YAML file or a JSON environment variable. Note that these options are mutually exclusive.

#### YAML Configuration

Create a `config.yaml` file and set the `MCP_CONFIG_PATH` environment variable to its path.

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

#### JSON Environment Variable

Set the `MCP_CONFIG_JSON` environment variable to a JSON string.

```bash
export MCP_CONFIG_JSON='{"prompts":{"summarize":{"defaults":{"tone":"concise"}},"clients":{"acme":{"tone":"detailed"}}}}}'
```

--- 

## 🧪 Testing

To run the test suite, use the following command:

```bash
# Using uv (recommended)
uv run python -m pytest -q

# Using pytest directly
pytest
```

After making any changes to the code, it is important to run the tests to ensure that everything is still working correctly.

--- 

## 🐳 Docker

You can build and run the server in a Docker container.

```bash
# Build the image
docker build -t mcp-server-openai:0.2.0 .

# Run the container
docker run --rm -p 8000:8000 mcp-server-openai:0.2.0
```

--- 

## 🛠️ Development

This project uses `make` to streamline common development tasks.

```bash
make check       # Run all checks
make fmt         # Format code
make lint        # Lint code
make test        # Run tests
```

--- 

## 📁 Project Structure

```
src/mcp_server_openai/
├── __main__.py              # CLI entrypoint
├── main.py                  # Main application logic
├── server.py                # FastMCP app factory + auto-discovery
├── http_server.py           # Legacy HTTP/SSE server (Starlette)
├── streaming_http.py        # Modern streamable HTTP server with advanced features
├── enhanced_server.py       # Enhanced server runner with graceful shutdown
├── server_config.py         # Configuration management system
├── error_handling.py        # Comprehensive error handling and monitoring
├── config.py                # YAML/JSON config loader
├── logging_utils.py         # Structured JSON logging
├── progress.py              # Modern progress tracking with ETA & hierarchical support
├── tools/
│   ├── __init__.py
│   ├── math_tools.py        # Mathematical operations
│   ├── web_tools.py         # Web content fetching
│   └── content_creator.py   # PowerPoint generation
├── resources/
│   ├── __init__.py
│   └── health.py            # Health check resources
└── prompts/
    ├── __init__.py          # Enhanced prompt system exports
    ├── manager.py           # Modern prompt manager with advanced features
    ├── summarize.py         # Summarization prompts
    ├── content_create.py    # Content creation prompts
    ├── README.md           # Prompt system documentation
    └── templates/
        ├── base.j2         # Base template with inheritance
        ├── summarize.j2    # Summarization template
        └── content_create.j2 # Content creation template

scripts/
├── call_tool.py             # CLI tool caller
├── cli.sh                   # Shell utilities
├── preflight.py             # Code quality checks
└── run.sh                   # Runtime scripts

tests/                       # Comprehensive test suite
├── conftest.py
├── test_*.py               # Unit tests for all modules
├── test_streaming_http.py  # Tests for modern streaming features
└── ...
```

--- 

## 📈 Changelog

### v0.2.0 (Current)

- **Milestone 2: Registry & Prompts**
  - Implemented auto-discovery of tools.
  - Added a YAML/JSON config loader with per-client prompt variables.
  - Integrated Jinja2-based prompt templates with client overrides.
  - Implemented structured JSON logging with request lifecycle tracking.
- **Enhanced Prompt Management System v2.0**
  - Developed a modern, robust prompt management system.
  - Added template validation and health checks.
  - Implemented advanced caching with TTL and invalidation strategies.
- **Milestone 3.1: HTTP/SSE**
  - Implemented Server-Sent Events streaming with keep-alive.
  - Added health and info endpoints for monitoring.
- **Milestone 3.2: Progress Tracking**
  - Implemented a modern progress tracking system with percentage & ETA calculation.
  - Added hierarchical progress support for complex workflows.
- **Milestone 3.3: Modern Streamable HTTP**
  - Added HTTP/2 support with ALPN negotiation.
  - Implemented enhanced Server-Sent Events with multiplexing and capability negotiation.
  - Integrated WebSocket for real-time bidirectional communication.
- **Code Quality & Type Safety Improvements**
  - Implemented comprehensive mypy type checking with strict compliance.
  - Enhanced type annotations across all modules.

--- 

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch: `git checkout -b feature-name`
3.  Make your changes, following the existing code style.
4.  Run the quality checks: `make check`
5.  Submit a pull request.

--- 

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

--- 

*Built with ❤️ using FastMCP and the Model Context Protocol*