"""
Enhanced prompt management system for MCP Server OpenAI.

This package provides:
- Modern, robust prompt manager with advanced features
- Template-based prompt generation with Jinja2
- Client-specific prompt customization
- Async support and performance metrics
- Comprehensive error handling and validation
"""

from .content_create import (
    create_content_prompt,
    create_content_prompt_async,
    get_content_create_help,
    register_content_create,
)
from .manager import (
    ConfigurationError,
    PromptManager,
    PromptManagerError,
    TemplateNotFoundError,
    TemplateRenderError,
    get_prompt_manager,
    render,
    render_async,
)
from .summarize import (
    get_summarize_help,
    register_summarize,
    summarize,
    summarize_async,
    summarize_prompt,
)

__all__ = [
    # Core prompt manager
    "PromptManager",
    "get_prompt_manager",
    "render",
    "render_async",
    # Error classes
    "PromptManagerError",
    "TemplateNotFoundError",
    "TemplateRenderError",
    "ConfigurationError",
    # Summarize prompts
    "summarize",
    "summarize_async",
    "summarize_prompt",
    "register_summarize",
    "get_summarize_help",
    # Content creation prompts
    "create_content_prompt",
    "create_content_prompt_async",
    "register_content_create",
    "get_content_create_help",
]

# Version info
__version__ = "2.0.0"
