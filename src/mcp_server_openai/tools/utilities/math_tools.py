"""
Mathematical tools.

Defines pure functions (unit-testable) and registers MCP tools that wrap them.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid importing SDK at runtime during tests
    from fastmcp import FastMCP


def add_numbers(a: float, b: float) -> float:
    """Return a + b."""
    return a + b


def subtract_numbers(a: float, b: float) -> float:
    """Return a - b."""
    return a - b


def register(mcp: "FastMCP") -> None:
    """
    Register math tools on the provided FastMCP instance.
    """

    @mcp.tool(name="math.add", description="Add two numbers and return the sum.")
    def add(a: float, b: float) -> float:
        return add_numbers(a, b)

    @mcp.tool(name="math.sub", description="Subtract b from a and return the result.")
    def sub(a: float, b: float) -> float:
        return subtract_numbers(a, b)
