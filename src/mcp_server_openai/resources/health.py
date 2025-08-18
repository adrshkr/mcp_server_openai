"""
Health check resource.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid importing SDK at runtime during tests
    from fastmcp import FastMCP


def ping() -> str:
    """Return a simple 'ok' indicator."""
    return "ok"


def register(mcp: "FastMCP") -> None:
    """
    Register the health resource at 'health://ping'.
    """

    @mcp.resource("health://ping", description="Simple health check returning 'ok'.")
    def _ping() -> str:
        return ping()
