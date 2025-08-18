from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template

from .. import config

# templates live next to this module under "templates/"
_THIS_DIR = Path(__file__).parent.resolve()
_TEMPLATE_DIR = _THIS_DIR / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=False,  # prompts are plain text
    trim_blocks=False,
    lstrip_blocks=False,
)


def _dev_mode() -> bool:
    # When DEV=1, bypass template cache for easy iteration.
    return os.environ.get("DEV") == "1"


@lru_cache(maxsize=64)
def _get_template(name: str) -> Template:
    return _env.get_template(f"{name}.j2")


def render(prompt_name: str, params: dict[str, Any], client_id: str | None = None) -> str:
    """
    Render a prompt by merging config defaults + client overrides + explicit params.
    Explicit params (params) win over config.
    """
    if _dev_mode():
        _get_template.cache_clear()
        config.load_config.cache_clear()

    tmpl = _get_template(prompt_name)
    merged = {**config.get_prompt_vars(prompt_name, client_id), **(params or {})}
    return tmpl.render(merged)
