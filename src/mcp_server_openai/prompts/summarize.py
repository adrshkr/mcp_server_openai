"""
Enhanced summarize prompt functionality with robust error handling.

This module provides both the legacy simple prompt function and integration
with the modern PromptManager for advanced template-based prompts.
"""

from __future__ import annotations

from typing import Any

from .manager import get_prompt_manager, render, render_async


def summarize_prompt(topic: str, tone: str = "concise") -> str:
    """
    Legacy/simple prompt generator used as a fallback
    when the file-based PromptManager isn't available.

    Args:
        topic: The topic to summarize
        tone: The tone of the summary (concise, detailed, etc.)

    Returns:
        A simple prompt string
    """
    return f"Please provide a {tone} summary of the topic: {topic}."


def summarize(topic: str, tone: str = "concise", client_id: str | None = None, **kwargs: Any) -> str:
    """
    Render the 'summarize' prompt using the PromptManager (if available),
    otherwise return the legacy summarize_prompt.

    Args:
        topic: The topic to summarize
        tone: The tone of the summary
        client_id: Client ID for client-specific overrides
        **kwargs: Additional parameters to pass to the template

    Returns:
        Rendered prompt string

    Raises:
        Exception: If prompt rendering fails and no fallback is available
    """
    try:
        # Try to use the modern prompt manager
        params: dict[str, Any] = {"topic": topic, "tone": tone}
        params.update(kwargs)

        # Use the new render function
        return render("summarize", params=params, client_id=client_id)

    except Exception as e:
        # Log the error but don't fail completely
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to render summarize prompt with PromptManager: {e}")

        # Fall back to legacy function
        return summarize_prompt(topic, tone=tone)


async def summarize_async(topic: str, tone: str = "concise", client_id: str | None = None, **kwargs: Any) -> str:
    """
    Async version of summarize function.

    Args:
        topic: The topic to summarize
        tone: The tone of the summary
        client_id: Client ID for client-specific overrides
        **kwargs: Additional parameters to pass to the template

    Returns:
        Rendered prompt string

    Raises:
        Exception: If prompt rendering fails and no fallback is available
    """
    try:
        # Try to use the modern prompt manager with async support
        params: dict[str, Any] = {"topic": topic, "tone": tone}
        params.update(kwargs)

        # Use the new async render function
        return await render_async("summarize", params=params, client_id=client_id)

    except Exception as e:
        # Log the error but don't fail completely
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to render summarize prompt with async PromptManager: {e}")

        # Fall back to sync version
        return summarize(topic, tone=tone, client_id=client_id, **kwargs)


def register_summarize(mcp: Any) -> None:
    """
    Register the summarize prompt with the MCP server.

    Args:
        mcp: The FastMCP instance to register with
    """
    try:
        # Get the prompt manager to check if it's available
        get_prompt_manager()

        # Register the summarize prompt as a resource
        @mcp.resource("prompts://summarize", description="Generate summarize prompts with template support.")
        def summarize_resource(topic: str, tone: str = "concise", client_id: str | None = None, **kwargs: Any) -> str:
            """Resource endpoint for summarize prompts."""
            return summarize(topic, tone=tone, client_id=client_id, **kwargs)

        # Also register an async version if supported
        if hasattr(mcp, "resource_async"):

            @mcp.resource_async("prompts://summarize/async", description="Async version of summarize prompts.")
            async def summarize_async_resource(
                topic: str, tone: str = "concise", client_id: str | None = None, **kwargs: Any
            ) -> str:
                """Async resource endpoint for summarize prompts."""
                return await summarize_async(topic, tone=tone, client_id=client_id, **kwargs)

        import logging

        logger = logging.getLogger(__name__)
        logger.info("Summarize prompt registered successfully with MCP server")

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to register summarize prompt: {e}")
        # Don't fail the registration, just log the warning


def get_summarize_help() -> str:
    """
    Get help information for the summarize prompt.

    Returns:
        Help string with usage information
    """
    return """
Summarize Prompt Help
====================

Usage:
  summarize(topic, tone="concise", client_id=None, **kwargs)

Parameters:
  topic (str): The topic to summarize (required)
  tone (str): Tone of the summary - "concise", "detailed", "formal", etc.
  client_id (str): Client ID for client-specific customizations
  **kwargs: Additional parameters like audience, style, bullets_min, bullets_max

Examples:
  summarize("AI trends", tone="detailed", audience="executives")
  summarize("Machine learning", client_id="acme", style="technical")

Client-specific overrides can be configured in the MCP config file.
"""
