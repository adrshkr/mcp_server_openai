"""
Config loader for client-specific prompt variables and tool settings.

Sources:
  - YAML file path via env var: MCP_CONFIG_PATH
  - Or minimal inline JSON via env var: MCP_CONFIG_JSON

Shape (YAML):
prompts:
  summarize:
    defaults:
      tone: concise
    clients:
      acme:
        tone: detailed
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import yaml


def _load_yaml(path: str) -> Dict[str, Any]:
  with open(path, "r", encoding="utf-8") as f:
    return yaml.safe_load(f) or {}


def _load_env_json(var: str) -> Dict[str, Any]:
  raw = os.environ.get(var, "").strip()
  if not raw:
    return {}
  try:
    return json.loads(raw)
  except json.JSONDecodeError:
    return {}


def load_config() -> Dict[str, Any]:
  """
  Load configuration from MCP_CONFIG_PATH (YAML) or MCP_CONFIG_JSON.
  Returns {} if nothing found or parse failed.
  """
  path = os.environ.get("MCP_CONFIG_PATH", "").strip()
  if path and os.path.exists(path):
    try:
      return _load_yaml(path)
    except Exception:
      return {}

  env_json = _load_env_json("MCP_CONFIG_JSON")
  if env_json:
    return env_json

  return {}


def get_prompt_vars(prompt_name: str, client_id: Optional[str]) -> Dict[str, Any]:
  """
  Resolve vars for a prompt, merging defaults with client overrides.
  """
  cfg = load_config()
  prompts = cfg.get("prompts", {})
  p = prompts.get(prompt_name, {})
  defaults = p.get("defaults", {}) or {}
  if client_id:
    client_over = (p.get("clients", {}) or {}).get(client_id, {})
  else:
    client_over = {}
  merged = {**defaults, **client_over}
  return merged