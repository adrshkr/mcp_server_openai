"""
Simplified tool registration system for MCP Server OpenAI.

This module provides a centralized way to discover, register, and manage tools
with better error handling and validation.
"""

import importlib
import inspect
from pathlib import Path
from typing import Any

from .error_handler import ConfigurationError
from .logging import get_logger

logger = get_logger("tool_registry")


class ToolInfo:
    """Information about a registered tool."""

    def __init__(
        self,
        name: str,
        tool_class: type,
        description: str,
        category: str,
        version: str = "1.0.0",
        enabled: bool = True,
        dependencies: list[str] | None = None,
    ):
        self.name = name
        self.tool_class = tool_class
        self.description = description
        self.category = category
        self.version = version
        self.enabled = enabled
        self.dependencies = dependencies or []
        self.instance: Any | None = None

    def __repr__(self) -> str:
        return f"ToolInfo(name='{self.name}', category='{self.category}', enabled={self.enabled})"


class ToolRegistry:
    """Centralized tool registration and management system."""

    def __init__(self):
        self.tools: dict[str, ToolInfo] = {}
        self.categories: dict[str, list[str]] = {}
        self.logger = get_logger("tool_registry")

    def register_tool(
        self,
        name: str,
        tool_class: type,
        description: str,
        category: str = "general",
        version: str = "1.0.0",
        enabled: bool = True,
        dependencies: list[str] | None = None,
        force: bool = False,
    ) -> None:
        """Register a tool with validation."""

        # Check if tool already exists
        if name in self.tools and not force:
            raise ConfigurationError(f"Tool '{name}' is already registered")

        # Validate tool class
        if not inspect.isclass(tool_class):
            raise ConfigurationError(f"Tool '{name}' must be a class, got {type(tool_class)}")

        # Check dependencies
        if dependencies:
            missing_deps = [dep for dep in dependencies if dep not in self.tools]
            if missing_deps:
                self.logger.warning(f"Tool '{name}' has missing dependencies: {missing_deps}")

        # Create tool info
        tool_info = ToolInfo(
            name=name,
            tool_class=tool_class,
            description=description,
            category=category,
            version=version,
            enabled=enabled,
            dependencies=dependencies,
        )

        # Register tool
        self.tools[name] = tool_info

        # Update categories
        if category not in self.categories:
            self.categories[category] = []
        if name not in self.categories[category]:
            self.categories[category].append(name)

        self.logger.info(f"Registered tool '{name}' in category '{category}'")

    def unregister_tool(self, name: str) -> None:
        """Unregister a tool."""
        if name not in self.tools:
            raise ConfigurationError(f"Tool '{name}' is not registered")

        tool_info = self.tools[name]

        # Remove from category
        if tool_info.category in self.categories:
            if name in self.categories[tool_info.category]:
                self.categories[tool_info.category].remove(name)

            # Remove empty category
            if not self.categories[tool_info.category]:
                del self.categories[tool_info.category]

        # Remove tool
        del self.tools[name]

        self.logger.info(f"Unregistered tool '{name}'")

    def get_tool(self, name: str) -> ToolInfo | None:
        """Get tool information by name."""
        return self.tools.get(name)

    def get_tool_instance(self, name: str) -> Any:
        """Get or create tool instance."""
        tool_info = self.get_tool(name)
        if not tool_info:
            raise ConfigurationError(f"Tool '{name}' is not registered")

        if not tool_info.enabled:
            raise ConfigurationError(f"Tool '{name}' is disabled")

        # Create instance if not exists
        if tool_info.instance is None:
            try:
                tool_info.instance = tool_info.tool_class()
                self.logger.debug(f"Created instance for tool '{name}'")
            except Exception as e:
                self.logger.error(f"Failed to create instance for tool '{name}'", error=e)
                raise ConfigurationError(f"Failed to create tool '{name}': {e}") from e

        return tool_info.instance

    def list_tools(self, category: str | None = None, enabled_only: bool = True) -> list[ToolInfo]:
        """List registered tools."""
        tools = list(self.tools.values())

        if category:
            tools = [t for t in tools if t.category == category]

        if enabled_only:
            tools = [t for t in tools if t.enabled]

        return tools

    def list_categories(self) -> list[str]:
        """List all tool categories."""
        return list(self.categories.keys())

    def enable_tool(self, name: str) -> None:
        """Enable a tool."""
        tool_info = self.get_tool(name)
        if not tool_info:
            raise ConfigurationError(f"Tool '{name}' is not registered")

        tool_info.enabled = True
        self.logger.info(f"Enabled tool '{name}'")

    def disable_tool(self, name: str) -> None:
        """Disable a tool."""
        tool_info = self.get_tool(name)
        if not tool_info:
            raise ConfigurationError(f"Tool '{name}' is not registered")

        tool_info.enabled = False
        # Clear instance to free resources
        tool_info.instance = None
        self.logger.info(f"Disabled tool '{name}'")

    def discover_tools(self, package_path: str, category: str = "auto") -> int:
        """Auto-discover tools in a package with better error handling."""

        discovered_count = 0

        try:
            # Convert string path to Path object
            if isinstance(package_path, str):
                if package_path.startswith("src/"):
                    # Handle relative paths from project root
                    base_path = Path(__file__).parent.parent.parent.parent
                    full_path = base_path / package_path
                else:
                    full_path = Path(package_path)
            else:
                full_path = package_path

            if not full_path.exists():
                self.logger.warning(f"Package path does not exist: {full_path}")
                return 0

            # Find Python files
            python_files = list(full_path.glob("**/*.py"))

            for py_file in python_files:
                if py_file.name.startswith("__"):
                    continue

                try:
                    # Convert file path to module name
                    relative_path = py_file.relative_to(full_path.parent)
                    module_name = str(relative_path.with_suffix("")).replace("/", ".").replace("\\", ".")

                    # Import module
                    module = importlib.import_module(module_name)

                    # Look for tool classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        # Check if it's a tool class (basic heuristic)
                        if (
                            inspect.isclass(attr)
                            and not attr_name.startswith("_")
                            and hasattr(attr, "__module__")
                            and attr.__module__ == module_name
                        ):
                            # Determine category
                            if category == "auto":
                                if "generator" in module_name.lower():
                                    tool_category = "generators"
                                elif "integration" in module_name.lower():
                                    tool_category = "integrations"
                                elif "utility" in module_name.lower():
                                    tool_category = "utilities"
                                else:
                                    tool_category = "general"
                            else:
                                tool_category = category

                            # Register tool
                            tool_name = f"{tool_category}.{attr_name.lower()}"
                            description = getattr(attr, "__doc__", f"Auto-discovered tool: {attr_name}")

                            try:
                                self.register_tool(
                                    name=tool_name,
                                    tool_class=attr,
                                    description=description.strip() if description else f"Tool: {attr_name}",
                                    category=tool_category,
                                    force=True,  # Allow overwriting during discovery
                                )
                                discovered_count += 1

                            except Exception as e:
                                self.logger.warning(f"Failed to register tool {tool_name}", error=e)

                except Exception as e:
                    self.logger.warning(f"Failed to process file {py_file}", error=e)
                    continue

        except Exception as e:
            self.logger.error(f"Tool discovery failed for {package_path}", error=e)
            return 0

        self.logger.info(f"Discovered {discovered_count} tools in {package_path}")
        return discovered_count

    def validate_dependencies(self) -> list[str]:
        """Validate all tool dependencies."""
        issues = []

        for tool_name, tool_info in self.tools.items():
            if not tool_info.dependencies:
                continue

            for dep in tool_info.dependencies:
                if dep not in self.tools:
                    issues.append(f"Tool '{tool_name}' depends on missing tool '{dep}'")
                elif not self.tools[dep].enabled:
                    issues.append(f"Tool '{tool_name}' depends on disabled tool '{dep}'")

        return issues

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        enabled_tools = [t for t in self.tools.values() if t.enabled]

        return {
            "total_tools": len(self.tools),
            "enabled_tools": len(enabled_tools),
            "disabled_tools": len(self.tools) - len(enabled_tools),
            "categories": len(self.categories),
            "tools_by_category": {
                cat: len([t for t in tools if self.tools[t].enabled]) for cat, tools in self.categories.items()
            },
        }


# Global tool registry instance
_global_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _global_registry


def register_tool(name: str, tool_class: type, description: str, category: str = "general", **kwargs) -> None:
    """Convenience function to register a tool."""
    _global_registry.register_tool(name, tool_class, description, category, **kwargs)


def get_tool_instance(name: str) -> Any:
    """Convenience function to get a tool instance."""
    return _global_registry.get_tool_instance(name)
