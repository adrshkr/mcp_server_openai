from __future__ import annotations

import importlib
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any


def _load_yaml_dict(path: Path) -> dict[str, Any]:
    """
    Load a YAML file into a dict without importing PyYAML at type-check time.
    If PyYAML isn't installed but MCP_CONFIG_PATH is set, we raise a clear error.
    """
    yaml_mod: Any
    try:
        yaml_mod = importlib.import_module("yaml")  # runtime import, typed as Any
    except Exception as exc:
        raise RuntimeError("PyYAML is required when MCP_CONFIG_PATH is set; install 'PyYAML'.") from exc

    with path.open("r", encoding="utf-8") as fh:
        data = yaml_mod.safe_load(fh)  # Any
    return dict(data or {})


@lru_cache(maxsize=1)
def load_config() -> dict[str, Any]:
    """
    Loads config from MCP_CONFIG_JSON or MCP_CONFIG_PATH.
    Falls back to an empty dict when not provided or on parse errors.
    """
    env_json = os.environ.get("MCP_CONFIG_JSON")
    env_path = os.environ.get("MCP_CONFIG_PATH")

    if env_json:
        try:
            data = json.loads(env_json)
            return dict(data or {})
        except Exception:
            # Silently fall back to empty on bad JSON; avoids breaking dev flows
            return {}

    if env_path:
        p = Path(env_path)
        if p.is_file():
            try:
                return _load_yaml_dict(p)
            except Exception:
                # Also fall back to empty if YAML load fails
                return {}

    return {}


def get_config() -> dict[str, Any]:
    """
    Public accessor for the (cached) merged config.
    """
    # Create a cache key based on environment variables to ensure proper invalidation
    cache_key = (os.environ.get("MCP_CONFIG_JSON"), os.environ.get("MCP_CONFIG_PATH"))
    return _load_config_with_cache(cache_key)


@lru_cache(maxsize=1)
def _load_config_with_cache(cache_key: tuple[str | None, str | None]) -> dict[str, Any]:
    """
    Internal cached function that loads config based on cache key.
    """
    env_json, env_path = cache_key

    if env_json:
        try:
            data = json.loads(env_json)
            return dict(data or {})
        except Exception:
            # Silently fall back to empty on bad JSON; avoids breaking dev flows
            return {}

    if env_path:
        p = Path(env_path)
        if p.is_file():
            try:
                result = _load_yaml_dict(p)
                return result
            except Exception:
                # Also fall back to empty if YAML load fails
                return {}

    return {}


def get_prompt_vars(prompt_name: str, client_id: str | None = None) -> dict[str, Any]:
    """
    Retrieve merged variables for a given prompt.

    Merge order (earlier can be overridden by later):
      1) defaults
      2) client-specific overrides (if client_id provided)
    """
    cfg = get_config()
    prompt_cfg = dict(cfg.get("prompts", {}).get(prompt_name, {}) or {})

    defaults = dict(prompt_cfg.get("defaults", {}) or {})
    client_overrides: dict[str, Any] = {}
    if client_id:
        client_overrides = dict((prompt_cfg.get("clients", {}) or {}).get(client_id, {}) or {})

    merged = {**defaults, **client_overrides}
    return merged
