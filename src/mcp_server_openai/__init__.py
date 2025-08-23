"""
MCP Server OpenAI - A Model Context Protocol server with OpenAI integration.

This package provides tools for:
- Content validation and quality assessment
- MCP protocol implementation
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .tools.mcp_content_validation import register as register_content_validation_tools

__all__ = [
    "register_content_validation_tools",
]
