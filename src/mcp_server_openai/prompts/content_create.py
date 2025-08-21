"""
Content creation prompt functionality with template support.

This module provides prompts for creating various types of content
including PowerPoint presentations, reports, and other deliverables.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .manager import render, render_async


def create_content_prompt(
    client_name: str,
    project_name: str,
    source_content_type: str,
    source_content_details: Sequence[str],
    target_content_type: str,
    number_of_slides: int,
    content_brief: str,
    client_id: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Generate a content creation prompt using the PromptManager.

    Args:
        client_name: Name of the client
        project_name: Name of the project
        source_content_type: Type of source content (e.g., "Highlight", "Report")
        source_content_details: List of source content details
        target_content_type: Type of content to create (e.g., "PPT", "Report")
        number_of_slides: Number of slides for presentations
        content_brief: Brief description of the content to create
        client_id: Client ID for client-specific customizations
        **kwargs: Additional parameters like style, tone, audience

    Returns:
        Rendered prompt string

    Raises:
        Exception: If prompt rendering fails
    """
    try:
        # Prepare parameters for the template
        params: dict[str, Any] = {
            "client_name": client_name,
            "project_name": project_name,
            "source_content_type": source_content_type,
            "source_content_details": list(source_content_details),
            "target_content_type": target_content_type,
            "number_of_slides": number_of_slides,
            "content_brief": content_brief,
        }
        params.update(kwargs)

        # Use the content_create template
        return render("content_create", params=params, client_id=client_id)

    except Exception as e:
        # Fall back to a simple prompt if template rendering fails
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to render content creation prompt: {e}")

        return _fallback_content_prompt(
            client_name,
            project_name,
            source_content_type,
            source_content_details,
            target_content_type,
            number_of_slides,
            content_brief,
            **kwargs,
        )


async def create_content_prompt_async(
    client_name: str,
    project_name: str,
    source_content_type: str,
    source_content_details: Sequence[str],
    target_content_type: str,
    number_of_slides: int,
    content_brief: str,
    client_id: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Async version of create_content_prompt.

    Args:
        client_name: Name of the client
        project_name: Name of the project
        source_content_type: Type of source content
        source_content_details: List of source content details
        target_content_type: Type of content to create
        number_of_slides: Number of slides for presentations
        content_brief: Brief description of the content to create
        client_id: Client ID for client-specific customizations
        **kwargs: Additional parameters

    Returns:
        Rendered prompt string
    """
    try:
        # Prepare parameters for the template
        params: dict[str, Any] = {
            "client_name": client_name,
            "project_name": project_name,
            "source_content_type": source_content_type,
            "source_content_details": list(source_content_details),
            "target_content_type": target_content_type,
            "number_of_slides": number_of_slides,
            "content_brief": content_brief,
        }
        params.update(kwargs)

        # Use the async render function
        return await render_async("content_create", params=params, client_id=client_id)

    except Exception as e:
        # Fall back to sync version
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to render async content creation prompt: {e}")

        return create_content_prompt(
            client_name,
            project_name,
            source_content_type,
            source_content_details,
            target_content_type,
            number_of_slides,
            content_brief,
            client_id,
            **kwargs,
        )


def _fallback_content_prompt(
    client_name: str,
    project_name: str,
    source_content_type: str,
    source_content_details: Sequence[str],
    target_content_type: str,
    number_of_slides: int,
    content_brief: str,
    **kwargs: Any,
) -> str:
    """
    Fallback content creation prompt when template rendering fails.

    Args:
        client_name: Name of the client
        project_name: Name of the project
        source_content_type: Type of source content
        source_content_details: List of source content details
        target_content_type: Type of content to create
        number_of_slides: Number of slides for presentations
        content_brief: Brief description of the content to create
        **kwargs: Additional parameters

    Returns:
        Simple prompt string
    """
    style = kwargs.get("style", "professional")
    tone = kwargs.get("tone", "concise")
    audience = kwargs.get("audience", "stakeholders")

    prompt = f"""Create a {target_content_type} presentation for {client_name} project "{project_name}".

Source Content Type: {source_content_type}
Source Details:
"""

    for detail in source_content_details:
        prompt += f"- {detail}\n"

    prompt += f"""
Content Brief: {content_brief}

Requirements:
- Create {number_of_slides} slides
- Use {style} style with {tone} tone
- Target audience: {audience}
- Focus on key achievements and actionable next steps
- Structure logically with clear sections

Please provide a well-organized {target_content_type} that effectively communicates the key points."""

    return prompt


def register_content_create(mcp: Any) -> None:
    """
    Register the content creation prompt with the MCP server.

    Args:
        mcp: The FastMCP instance to register with
    """
    try:
        # Register the content creation prompt as a resource
        @mcp.resource(
            "prompts://content_create", description="Generate content creation prompts with template support."
        )
        def content_create_resource(
            client_name: str,
            project_name: str,
            source_content_type: str,
            source_content_details: list[str],
            target_content_type: str,
            number_of_slides: int,
            content_brief: str,
            client_id: str | None = None,
            **kwargs: Any,
        ) -> str:
            """Resource endpoint for content creation prompts."""
            return create_content_prompt(
                client_name,
                project_name,
                source_content_type,
                source_content_details,
                target_content_type,
                number_of_slides,
                content_brief,
                client_id,
                **kwargs,
            )

        # Also register an async version if supported
        if hasattr(mcp, "resource_async"):

            @mcp.resource_async(
                "prompts://content_create/async", description="Async version of content creation prompts."
            )
            async def content_create_async_resource(
                client_name: str,
                project_name: str,
                source_content_type: str,
                source_content_details: list[str],
                target_content_type: str,
                number_of_slides: int,
                content_brief: str,
                client_id: str | None = None,
                **kwargs: Any,
            ) -> str:
                """Async resource endpoint for content creation prompts."""
                return await create_content_prompt_async(
                    client_name,
                    project_name,
                    source_content_type,
                    source_content_details,
                    target_content_type,
                    number_of_slides,
                    content_brief,
                    client_id,
                    **kwargs,
                )

        import logging

        logger = logging.getLogger(__name__)
        logger.info("Content creation prompt registered successfully with MCP server")

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to register content creation prompt: {e}")
        # Don't fail the registration, just log the warning


def get_content_create_help() -> str:
    """
    Get help information for the content creation prompt.

    Returns:
        Help string with usage information
    """
    return """
Content Creation Prompt Help
===========================

Usage:
  create_content_prompt(client_name, project_name, source_content_type,
                       source_content_details, target_content_type,
                       number_of_slides, content_brief, client_id=None, **kwargs)

Parameters:
  client_name (str): Name of the client (required)
  project_name (str): Name of the project (required)
  source_content_type (str): Type of source content (e.g., "Highlight", "Report")
  source_content_details (Sequence[str]): List of source content details
  target_content_type (str): Type of content to create (e.g., "PPT", "Report")
  number_of_slides (int): Number of slides for presentations
  content_brief (str): Brief description of the content to create
  client_id (str): Client ID for client-specific customizations
  **kwargs: Additional parameters like style, tone, audience, language

Examples:
  create_content_prompt("Acme", "Q3", "Highlight", ["Market share +3%", "Beta launched"],
                       "PPT", 5, "Client-facing deck")
  create_content_prompt("TechCorp", "Annual", "Report", ["Revenue growth", "New products"],
                       "Report", 10, "Executive summary", client_id="techcorp", style="technical")

Client-specific overrides can be configured in the MCP config file.
"""
