"""
FastMCP application factory and exported app instance.

Registers tools, resources, and prompts. Use with the MCP CLI dev runner:

  uv run mcp dev src/mcp_server_openai/server.py:app
"""
from __future__ import annotations

import importlib
import pkgutil
from mcp.server.fastmcp import FastMCP  # match CLI SDK expectation

from mcp_server_openai.resources import register_health
from mcp_server_openai.prompts import register_summarize

import logging

logging.basicConfig(level=logging.WARNING)  # root
logging.getLogger("fastmcp").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

def _discover_and_register_tools(mcp: FastMCP) -> None:
  """
  Import all modules under mcp_server_openai.tools and call register(mcp) if present.
  """
  pkg_name = "mcp_server_openai.tools"
  pkg = importlib.import_module(pkg_name)
  for mod in pkgutil.iter_modules(pkg.__path__, pkg_name + "."):
    module = importlib.import_module(mod.name)
    reg = getattr(module, "register", None)
    if callable(reg):
      reg(mcp)


def create_app() -> FastMCP:
  """
  Build and return a FastMCP instance with all components registered.
  """
  mcp = FastMCP(name="mcp_server_openai")
  # Auto-discovered tools
  _discover_and_register_tools(mcp)
  # Resources
  register_health(mcp)
  # Prompts (with config support)
  register_summarize(mcp)
  return mcp


# Exported app for runners (stdio with MCP CLI)
app = create_app()