#!/usr/bin/env bash
set -euo pipefail
uv run mcp_server_openai -- "$@"
