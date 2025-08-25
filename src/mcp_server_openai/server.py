"""
FastMCP application factory and exported app instance.

Registers tools, resources, and prompts. Use with the MCP CLI dev runner:

  uv run mcp dev src/mcp_server_openai/server.py:app
"""

from __future__ import annotations

import importlib
import logging
import pkgutil

from mcp.server.fastmcp import FastMCP  # match CLI SDK expectation

from mcp_server_openai.core.config import get_config
from mcp_server_openai.core.logging import get_logger, setup_logging
from mcp_server_openai.core.tool_registry import get_tool_registry
from mcp_server_openai.monitoring.inline_display import get_display_manager
from mcp_server_openai.prompts import register_summarize
from mcp_server_openai.resources import register_health

# Initialize core systems
config = get_config()
logger = get_logger("server")

# Setup logging based on configuration
setup_logging(
    level=getattr(logging, config.server.log_level), log_file=config.logs_dir / "mcp_server.log", include_console=True
)

# Configure external library logging
logging.getLogger("fastmcp").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


def _discover_and_register_tools(mcp: FastMCP) -> None:
    """
    Import all modules under mcp_server_openai.tools and call register(mcp) if present.
    Also register tools with the unified tool registry.
    """
    tool_registry = get_tool_registry()

    # Auto-discover tools in the tools directory
    tools_discovered = tool_registry.discover_tools("src/mcp_server_openai/tools")
    logger.info(f"Discovered {tools_discovered} tools in tool registry")

    # Register tools with FastMCP
    pkg_name = "mcp_server_openai.tools"
    try:
        pkg = importlib.import_module(pkg_name)
        registered_count = 0

        for mod in pkgutil.iter_modules(pkg.__path__, pkg_name + "."):
            try:
                module = importlib.import_module(mod.name)
                reg = getattr(module, "register", None)
                if callable(reg):
                    reg(mcp)
                    registered_count += 1
                    logger.debug(f"Registered FastMCP tools from {mod.name}")
            except Exception as e:
                logger.warning(f"Failed to register tools from {mod.name}", error=e)

        logger.info(f"Registered {registered_count} FastMCP tool modules")

    except Exception as e:
        logger.error("Failed to discover FastMCP tools", error=e)


def create_app() -> FastMCP:
    """
    Build and return a FastMCP instance with all components registered.
    """
    logger.info("Creating FastMCP application")

    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")

        # Create FastMCP instance
        mcp = FastMCP(name="mcp_server_openai")

        # Auto-discovered tools
        _discover_and_register_tools(mcp)

        # Resources
        register_health(mcp)
        logger.debug("Registered health resources")

        # Prompts (with config support)
        register_summarize(mcp)
        logger.debug("Registered summarize prompts")

        # Initialize monitoring
        if config.features.enable_monitoring:
            _setup_monitoring(mcp)

        logger.info("FastMCP application created successfully")
        return mcp

    except Exception as e:
        logger.error("Failed to create FastMCP application", error=e)
        raise


def _setup_monitoring(mcp: FastMCP) -> None:
    """Setup monitoring and usage tracking."""
    try:
        # Initialize display manager (this also initializes the usage tracker)
        get_display_manager()

        # Note: Initial usage logging will happen on first request

        logging.getLogger("mcp.monitoring").info("Monitoring system initialized")
    except Exception as e:
        logging.getLogger("mcp.monitoring").warning(f"Failed to initialize monitoring: {e}")


# Exported app for runners (stdio with MCP CLI)
app = create_app()
