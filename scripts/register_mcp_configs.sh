#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/mnt/c/Users/adars/PycharmProjects/PythonProject/mcp_server_openai"

# Cursor config (WSL user home)
CURSOR_CFG="$HOME/.cursor/cli-config.json"
mkdir -p "$HOME/.cursor"
if [[ -f "$CURSOR_CFG" ]]; then
  tmp=$(mktemp)
  jq ".mcpServers.mcp-openai-enhanced={\"command\":\"wsl.exe\",\"args\":[\"bash\",\"-lc\",\"cd $PROJECT_ROOT && uv run python -m mcp_server_openai --stdio\"],\"env\":{}}" "$CURSOR_CFG" > "$tmp" && mv "$tmp" "$CURSOR_CFG"
else
  cat > "$CURSOR_CFG" <<JSON
{
  "version": 1,
  "mcpServers": {
    "mcp-openai-enhanced": {
      "command": "wsl.exe",
      "args": ["bash","-lc","cd $PROJECT_ROOT && uv run python -m mcp_server_openai --stdio"],
      "env": {}
    }
  }
}
JSON
fi

# Claude Desktop config (Windows roaming)
WIN_CLAUDE_DIR="/mnt/c/Users/adars/AppData/Roaming/Claude"
WIN_CLAUDE_CFG="$WIN_CLAUDE_DIR/claude_desktop_config.json"
mkdir -p "$WIN_CLAUDE_DIR"
if [[ -f "$WIN_CLAUDE_CFG" ]]; then
  tmp=$(mktemp)
  jq ".mcpServers.mcp-openai-enhanced={\"command\":\"wsl.exe\",\"args\":[\"bash\",\"-lc\",\"cd $PROJECT_ROOT && uv run python -m mcp_server_openai --stdio\"],\"env\":{}}" "$WIN_CLAUDE_CFG" > "$tmp" && mv "$tmp" "$WIN_CLAUDE_CFG"
else
  cat > "$WIN_CLAUDE_CFG" <<JSON
{
  "mcpServers": {
    "mcp-openai-enhanced": {
      "command": "wsl.exe",
      "args": ["bash","-lc","cd $PROJECT_ROOT && uv run python -m mcp_server_openai --stdio"],
      "env": {}
    }
  }
}
JSON
fi

echo "MCP server registrations updated."
