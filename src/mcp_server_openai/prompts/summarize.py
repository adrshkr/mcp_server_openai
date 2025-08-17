"""
Summarization prompt with client-aware defaults.
"""
from typing import TYPE_CHECKING, Optional
from mcp_server_openai.config import get_prompt_vars

if TYPE_CHECKING:  # avoid requiring SDK at test collection
  from mcp.server.fastmcp import FastMCP


def summarize_prompt(topic: str, tone: str = "concise") -> str:
  """
  Return a templated instruction string asking for a summary.
  """
  return f"Please provide a {tone} summary of the topic: {topic}."


def register(mcp: "FastMCP") -> None:
  """
  Register the summarize prompt with the provided FastMCP instance.

  Note: We accept an optional client_id to demonstrate per-client overrides.
  """
  @mcp.prompt(name="summarize", description="Templated summary instruction.")
  def summarize(topic: str, tone: Optional[str] = None, client_id: Optional[str] = None) -> str:
    vars_ = get_prompt_vars("summarize", client_id)
    effective_tone = tone or vars_.get("tone", "concise")
    return summarize_prompt(topic, effective_tone)