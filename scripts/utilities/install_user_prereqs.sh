#!/usr/bin/env bash
set -euo pipefail

# User-level durable environment (no sudo)

# Ensure pipx is available
if ! command -v pipx >/dev/null 2>&1; then
  python3 -m pip install --user pipx
  python3 -m pipx ensurepath
fi

# Ensure uv is available for this project
if ! command -v uv >/dev/null 2>&1; then
  pipx install uv || python3 -m pip install --user uv
fi

# Ripgrep via cargo-binstall or fallback to binary
if ! command -v rg >/dev/null 2>&1; then
  echo "Please install ripgrep (rg) via your package manager for best performance."
fi

# Node via n (optional)
if ! command -v node >/dev/null 2>&1; then
  echo "Consider installing Node.js via n (no sudo):"
  echo "  curl -fsSL https://raw.githubusercontent.com/tj/n/master/bin/n | bash -s lts"
fi

echo "User-level prerequisites installed or instructions provided."
