from __future__ import annotations

import importlib
from typing import Any


def summarize_prompt(topic: str, tone: str = "concise") -> str:
    """
    Legacy/simple prompt generator used by tests and as a fallback
    when the file-based PromptManager isn't available.
    """
    return f"Please provide a {tone} summary of the topic: {topic}."


# Try to import the file-based PromptManager dynamically; if not present, we fall back.
try:
    _pm: Any = importlib.import_module("mcp_server_openai.prompts.manager")
except Exception:
    _pm = None


def summarize(topic: str, tone: str = "concise", client_id: str | None = None, **kwargs: Any) -> str:
    """
    Render the 'summarize' prompt using the PromptManager (if available),
    otherwise return the legacy summarize_prompt.
    """
    if _pm is None:
        return summarize_prompt(topic, tone=tone)

    params: dict[str, Any] = {"topic": topic, "tone": tone}
    params.update(kwargs)
    rendered = _pm.render("summarize", params=params, client_id=client_id)
    return str(rendered)


def register_summarize(mcp: Any) -> None:
    """
    Placeholder registration hook to keep the auto-discovery path stable.
    (Tests don't exercise this yet; keeping the symbol avoids import errors.)
    """
    return None
