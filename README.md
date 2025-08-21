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

- [Quick Start](#-quick-start)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Stdio Mode](#stdio-mode-with-mcp-dev-inspector)
  - [HTTP Mode](#http-mode-with-sse)
- [API Reference](#-api-reference)
- [Progress Tracking](#-progress-tracking)
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

### HTTP Mode with Modern Streaming

The server now includes a modern streamable HTTP implementation with advanced features:

```bash
# Start modern HTTP server
uv run uvicorn mcp_server_openai.streaming_http:app --host 0.0.0.0 --port 8000

# Or use enhanced server runner
uv run python -m mcp_server_openai.enhanced_server --host 0.0.0.0 --port 8000

# Health checks
curl http://127.0.0.1:8000/health    # Enhanced health with metrics
curl http://127.0.0.1:8000/info      # Server information
curl http://127.0.0.1:8000/metrics   # Performance metrics

# Server-Sent Events endpoint with multiplexing
curl -iN "http://127.0.0.1:8000/mcp/sse?client_id=local-test"

# WebSocket connection for real-time communication  
curl --include \
     --no-buffer \
     --header "Connection: Upgrade" \
     --header "Upgrade: websocket" \
     --header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     --header "Sec-WebSocket-Version: 13" \
     http://127.0.0.1:8000/mcp/ws

# Streaming data endpoint with compression
curl -H "Accept-Encoding: gzip" http://127.0.0.1:8000/stream
```

#### Modern Features

- **HTTP/2 Support**: ALPN negotiation for improved performance
- **Enhanced SSE**: Multiplexing, capability negotiation, and compression
- **WebSocket Integration**: Real-time bidirectional communication
- **Response Compression**: gzip, brotli, and deflate support
- **Rate Limiting**: Protection against abuse with slowapi
- **Security Headers**: Modern security headers and CORS configuration
- **Performance Monitoring**: Built-in metrics and health checks
- **Claude Usage Monitoring**: Comprehensive token usage and cost tracking
- **Graceful Shutdown**: Proper connection cleanup and signal handling

#### Claude Usage Monitoring & Cost Tracking

The server now includes comprehensive Claude API usage monitoring with cost tracking:

```bash
# Usage tracking endpoint with detailed cost analysis
curl http://127.0.0.1:8000/usage

# Real-time usage streaming via SSE
curl -N "http://127.0.0.1:8000/mcp/sse?client_id=usage-monitor"

# Enhanced metrics with Claude usage data
curl http://127.0.0.1:8000/metrics
```

**Monitoring Features:**
- **Token Usage Tracking**: Real-time tracking of input, output, and cache tokens
- **Cost Analysis**: Per-request and session cost monitoring with burn rate calculations
- **Rate Limiting**: Cost-aware rate limiting to prevent budget overruns
- **Progress Integration**: Cost tracking integrated with progress monitoring
- **Real-time Streaming**: Live usage updates via SSE and WebSocket connections
- **Configuration**: Environment-based configuration for limits and monitoring

**Environment Variables for Monitoring:**
```bash
# Enable/disable monitoring
export MCP_MONITORING_ENABLED=true

# Cost limits
export MCP_COST_HOURLY_MAX=10.0
export MCP_COST_DAILY_MAX=100.0
export MCP_COST_PER_REQUEST_MAX=1.0

# Rate limiting
export MCP_RATE_LIMITING_ENABLED=true

# Refresh intervals
export MCP_REFRESH_INTERVAL=30.0
```

#### JavaScript SSE Example

```javascript
// Enhanced SSE with multiplexing support
const es = new EventSource("http://127.0.0.1:8000/mcp/sse?client_id=local-test&multiplex=true");
es.addEventListener("ready", (e) => {
    const data = JSON.parse(e.data);
    console.log("Server capabilities:", data.server_capabilities);
    console.log("Session ID:", data.session_id);
});
es.addEventListener("heartbeat", (e) => {
    const data = JSON.parse(e.data);
    console.log("Heartbeat:", data.heartbeat, "Active clients:", data.active_clients);
});
es.onmessage = (e) => console.log("message", e.data);
es.onerror = (e) => console.error("sse error", e);
```

#### WebSocket Example

```javascript
const ws = new WebSocket("ws://127.0.0.1:8000/mcp/ws");
ws.onopen = () => {
    console.log("WebSocket connected");
    ws.send(JSON.stringify({type: "ping", data: "Hello Server"}));
};
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Received:", data);
};
ws.onclose = (event) => {
    console.log("WebSocket closed:", event.code, event.reason);
};
```

### Legacy HTTP Mode

```bash
# Start legacy HTTP server (still available)
uv run uvicorn mcp_server_openai.http_server:app --host 0.0.0.0 --port 8000
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

The server includes an enhanced prompt management system with advanced template capabilities.

#### Available Prompts

##### `summarize`
Advanced summarization prompt with client-specific customization.

**Parameters:**
```json
{
  "topic": "Large Language Models",
  "tone": "concise",
  "audience": "general",
  "bullets_min": 4,
  "bullets_max": 6,
  "style": "professional",
  "language": "en",
  "client_id": "acme"
}
```

##### `content_create`
Template-based content creation system with rich customization.

**Parameters:**
```json
{
  "content_type": "presentation",
  "topic": "AI Strategy",
  "audience": "executives",
  "tone": "professional",
  "client_id": "enterprise_client"
}
```

#### Enhanced Features

- **Advanced Jinja2 Templates**: Template inheritance, macros, and custom filters
- **Configuration Schema Validation**: Pydantic-based validation with comprehensive error handling
- **Performance Monitoring**: Built-in metrics and caching with TTL
- **Client-Specific Overrides**: Per-client customization with fallback defaults
- **Async Support**: Fully asynchronous template rendering
- **Template Health Checks**: Validation and error recovery systems
- **Advanced Caching**: TTL-based caching with invalidation strategies

---

## 📈 Progress Tracking

The server includes a modern progress tracking system that provides real-time monitoring, percentage tracking, ETA calculation, and hierarchical progress support.

### Key Features

- **Percentage Tracking**: Automatic progress calculation with configurable total steps
- **ETA Calculation**: Dynamic estimation of completion time based on current progress
- **Hierarchical Progress**: Parent/child relationships for complex workflows with subtasks
- **Real-time Events**: Event-driven progress updates with customizable listeners
- **Context Managers**: Automatic progress tracking with error handling
- **Thread Safety**: Safe for concurrent operations
- **JSON Logging Integration**: Seamless integration with structured logging system

### Basic Usage

```python
from mcp_server_openai.progress import create_progress_tracker

# Create a progress tracker
tracker = create_progress_tracker("web.fetch_url", "req-123", total_steps=4)

# Manual step tracking
tracker.step("initialize", {"url": "example.com"})        # 25% complete
tracker.step("fetch_data", {"status": "downloading"})     # 50% complete
tracker.update_progress(75.0, "processing_response")      # 75% complete
tracker.complete("finished", {"status": "success"})      # 100% complete
```

### Context Managers

```python
# Automatic step tracking with error handling
with tracker.step_context("http_request", {"url": "example.com"}):
    response = await client.get(url)
    # Progress automatically updated

# Async context manager support
async with tracker.async_step_context("process_data"):
    result = await process_large_dataset()
```

### Hierarchical Progress

```python
# Create parent tracker
main_task = create_progress_tracker("data_pipeline", "req-123", total_steps=3)

# Create subtasks
loader = main_task.create_subtask("data_loading", total_steps=2)
loader.step("load_config")
loader.step("load_data")
loader.complete("data_loaded")

processor = main_task.create_subtask("data_processing")
processor.update_progress(30.0, "validating")
processor.update_progress(100.0, "complete")

# Parent progress aggregates children
aggregated = main_task.get_aggregated_progress()  # Returns combined progress
```

### Progress Events

Progress tracking emits structured JSON events that integrate with the logging system:

```json
{
  "event_type": "progress_update",
  "tool": "web.fetch_url",
  "request_id": "req-123",
  "step": "http_request",
  "progress_percent": 50.0,
  "eta_ms": 1245.6,
  "elapsed_ms": 1230.2,
  "details": {
    "progress_id": "uuid-4",
    "parent_id": null,
    "url": "https://example.com"
  },
  "correlation_id": "trace-456"
}
```

### Custom Progress Listeners

```python
from mcp_server_openai.progress import ProgressListener, ProgressEvent

class CustomProgressListener:
    def on_progress_update(self, event: ProgressEvent) -> None:
        # Send to monitoring system, websocket, etc.
        print(f"Progress: {event.progress_percent}% - {event.step_name}")

# Add custom listener
tracker.add_listener(CustomProgressListener())
```

### Backwards Compatibility

The legacy `Progress` class interface is maintained for existing code:

```python
from mcp_server_openai.progress import Progress

# Legacy interface still works
progress = Progress("tool_name", "request_id")
progress.step("step_name", {"detail": "value"})
```

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
make check       # Full check: preflight + tests + mypy
make preflight   # Code formatting and linting
make fmt         # Format code with Black
make lint        # Lint with Ruff
make test        # Run tests
make run-http    # Start legacy HTTP server
make run-stream  # Start modern streaming HTTP server
make run-enhanced # Start enhanced server runner
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

### v0.2.0 - Current

**Milestone 2: Registry & Prompts**
- ✅ Auto-discovery of tools via `register(mcp)` pattern
- ✅ YAML/JSON config loader with per-client prompt variables  
- ✅ Jinja2-based prompt templates with client overrides
- ✅ Structured JSON logging with request lifecycle tracking

**Enhanced Prompt Management System v2.0**
- ✅ Modern, robust prompt management with advanced features
- ✅ Template validation and health checks
- ✅ Advanced caching with TTL and invalidation strategies
- ✅ Configuration schema validation with Pydantic
- ✅ Comprehensive error handling and recovery
- ✅ Async support with performance metrics
- ✅ Advanced Jinja2 features (inheritance, macros, custom filters)
- ✅ Client-specific prompt customization and overrides
- ✅ Template-based content creation system

**Milestone 3.1: HTTP/SSE**
- ✅ Server-Sent Events streaming with keep-alive
- ✅ Health and info endpoints for monitoring
- ✅ Cross-platform compatibility (Windows-friendly tests)
- ✅ Docker containerization support

**Milestone 3.2: Progress Tracking**
- ✅ Modern progress tracking system with percentage & ETA calculation
- ✅ Hierarchical progress support for complex workflows
- ✅ Real-time progress events with customizable listeners
- ✅ Context manager support for automatic progress tracking
- ✅ Thread-safe operations and backwards compatibility

**Milestone 3.3: Modern Streamable HTTP**
- ✅ HTTP/2 support with ALPN negotiation for improved performance
- ✅ Enhanced Server-Sent Events with multiplexing and capability negotiation
- ✅ WebSocket integration for real-time bidirectional communication
- ✅ Response compression support (gzip, brotli, deflate)
- ✅ Rate limiting protection with slowapi integration
- ✅ Modern security headers and CORS configuration
- ✅ Performance monitoring with built-in metrics and health checks
- ✅ Graceful shutdown with proper connection cleanup
- ✅ Circuit breaker and retry patterns for fault tolerance
- ✅ Enhanced server runner with signal handling

**Code Quality & Type Safety Improvements**
- ✅ Comprehensive mypy type checking with strict compliance
- ✅ Enhanced type annotations across all modules
- ✅ Fixed FastMCP compatibility issues
- ✅ Improved error handling and validation
- ✅ Added types-PyYAML for complete YAML type support
- ✅ Resolved all static analysis issues
- ✅ Enhanced development tooling and CI/CD pipeline

**Features:**
- 🔧 Mathematical operations (`math.add`, `math.sub`)
- 🌐 Web content fetching (`web.fetch_url`) with progress tracking
- 📄 PowerPoint generation (`content.create`)
- 🎯 Client-specific prompt customization
- 📊 Health monitoring resources
- 📈 Real-time progress tracking with ETA calculation

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
