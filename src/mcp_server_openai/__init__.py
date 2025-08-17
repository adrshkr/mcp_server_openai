"""
Top-level package for the MCP server.

Note: we do NOT import `.server` here to avoid importing the MCP SDK
at package import time (which breaks test collection if the SDK is not
installed yet). Runners should import `mcp_server_openai.server:app`
directly.
"""

__all__ = []
