#!/usr/bin/env bash
set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
  echo "Please run with sudo: sudo bash $0" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
  git gh ripgrep fd-find jq unzip wget curl build-essential \
  python3 python3-venv python3-pip pipx \
  sqlite3 redis-server ca-certificates gnupg lsb-release

# Install Node.js 20.x
if ! command -v node >/dev/null 2>&1 || [[ $(node -v | cut -d. -f1 | tr -d v) -lt 20 ]]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi

# Install Playwright system dependencies
npx --yes playwright install-deps || true

# Ensure pipx path for all users
pipx ensurepath || true

systemctl enable redis-server || true
systemctl start redis-server || true

echo "System prerequisites installed."
