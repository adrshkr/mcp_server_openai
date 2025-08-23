"""
MCP Server OpenAI - A Model Context Protocol server with OpenAI integration.

This package provides tools for:
- Content validation and quality assessment
- MCP protocol implementation
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Backwards compatibility: expose `streaming_http` at package root
# so references like `mcp_server_openai.streaming_http` continue to work
# after moving the module under `api/`.
import sys as _sys

from .api import streaming_http as streaming_http  # re-export module
from .tools.mcp_integrations.mcp_content_validation import register as register_content_validation_tools

__all__ = [
    "register_content_validation_tools",
    "streaming_http",
]

# Ensure importing as a submodule path is supported
_sys.modules[f"{__name__}.streaming_http"] = streaming_http
