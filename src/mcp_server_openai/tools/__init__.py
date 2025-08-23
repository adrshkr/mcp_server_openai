"""
Tool plug-ins for the MCP server.

Organized by functionality:
- generators: Content creation and generation tools
- mcp_integrations: MCP server integration tools
- utilities: General utility tools

Modules in this package are auto-discovered and must expose:
  def register(mcp: FastMCP) -> None
"""

# No explicit imports; discovery happens in server.create_app()
