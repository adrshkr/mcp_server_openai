"""
Tool plug-ins for the MCP server.

Modules in this package are auto-discovered and must expose:
  def register(mcp: FastMCP) -> None
"""

# No explicit imports; discovery happens in server.create_app()
