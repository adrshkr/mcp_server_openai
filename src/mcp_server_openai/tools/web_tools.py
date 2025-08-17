"""
Web utility tools.

Provides an async tool to fetch the text content of a URL with robust handling.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, Field
import httpx
import re
import json

# Use TYPE_CHECKING to avoid requiring the SDK during test collection
if TYPE_CHECKING:
  from mcp.server.fastmcp import FastMCP  # matches the MCP CLI SDK you are using


# ---- Structured result model (internal) --------------------------------------

class FetchResult(BaseModel):
  url: str = Field(..., description="Final (normalized) URL requested")
  status_code: Optional[int] = None
  content_type: Optional[str] = None
  headers: dict[str, str] = {}
  content_preview: str = ""
  truncated: bool = False
  elapsed_ms: Optional[float] = None
  error: Optional[str] = None


# ---- Helpers -----------------------------------------------------------------

def _normalize_url(raw: str) -> str:
  s = (raw or "").strip()
  # collapse inner whitespace runs then encode spaces
  s = re.sub(r"\s+", " ", s).replace(" ", "%20")
  if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", s):
    s = "https://" + s
  return s


async def fetch_url_content(
  url: str,
  timeout: float = 10.0,
  max_chars: int = 200_000,
  allow_redirects: bool = True,
  user_agent: Optional[str] = None,
) -> FetchResult:
  """
  Fetch 'url' and return a structured result. Never raises; errors are returned.
  """
  final_url = _normalize_url(url)
  headers = {}
  if user_agent:
    headers["User-Agent"] = user_agent

  try:
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=allow_redirects, headers=headers) as client:
      resp = await client.get(final_url)
      text = resp.text or ""
      preview = text[:max_chars]
      subset = {k.lower(): v for k, v in resp.headers.items()
                if k.lower() in ("content-type", "content-length", "server")}
      elapsed = float(getattr(resp, "elapsed", 0).total_seconds() * 1000) if getattr(resp, "elapsed", None) else None
      return FetchResult(
        url=str(resp.url),
        status_code=resp.status_code,
        content_type=resp.headers.get("content-type"),
        headers=subset,
        content_preview=preview,
        truncated=len(text) > max_chars,
        elapsed_ms=elapsed,
      )
  except httpx.HTTPError as e:
    return FetchResult(url=final_url, error=str(e))


def flatten_fetch_result(res: FetchResult) -> dict[str, str | int | bool | None]:
  """Convert FetchResult to a flat dict of primitives (inspector-compatible)."""
  return {
    "url": res.url,
    "status_code": int(res.status_code) if res.status_code is not None else None,
    "content_type": res.content_type or None,
    "headers_json": json.dumps(res.headers, ensure_ascii=False),  # stringify nested dict
    "content_preview": res.content_preview,
    "truncated": bool(res.truncated),
    "elapsed_ms": int(res.elapsed_ms) if isinstance(res.elapsed_ms, float) else None,
    "error": res.error or None,
  }


# ---- MCP registration --------------------------------------------------------

def register(mcp: "FastMCP") -> None:
  """
  Register the web fetching tool on the provided FastMCP instance.

  IMPORTANT: The MCP inspector only accepts primitive dict values.
  We therefore flatten the response and stringify complex types.
  """
  @mcp.tool(
    name="web.fetch_url",
    description="Fetch a URL and return a flat JSON result (status, headers_json, content preview)."
  )
  async def fetch_url(
    url: str,
    timeout: float = 10.0,
    max_chars: int = 200_000,
    allow_redirects: bool = True,
    user_agent: Optional[str] = None,
  ) -> dict[str, str | int | bool | None]:
    res = await fetch_url_content(
      url=url,
      timeout=timeout,
      max_chars=max_chars,
      allow_redirects=allow_redirects,
      user_agent=user_agent,
    )
    return flatten_fetch_result(res)
