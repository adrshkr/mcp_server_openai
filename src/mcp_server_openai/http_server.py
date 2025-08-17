from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Dict

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, StreamingResponse
from starlette.routing import Route


async def health(_: Request) -> PlainTextResponse:
  """Simple liveness check."""
  return PlainTextResponse("ok")


async def info(_: Request) -> JSONResponse:
  """Basic server info and advertised endpoints."""
  data: Dict[str, Any] = {
    "name": "mcp_server_openai",
    "env": {"python": None},
    "endpoints": {
      "health": "/health",
      "info": "/info",
      "mcp_sse": "/mcp/sse",
    },
    "notes": "SSE endpoint streams keep-alives and a ready event. Hook real MCP events in the next milestone.",
  }
  return JSONResponse(data)


async def _sse_generator(client_id: str | None) -> AsyncGenerator[bytes, None]:
  """
  Minimal Server-Sent Events stream.

  Sends:
    - an initial comment announcing connection,
    - a 'ready' event so clients can verify streaming,
    - periodic keep-alive comments so proxies keep the connection open.

  IMPORTANT: Do not write in the CancelledError path; just propagate.
  """
  # Initial connection comment and a 'ready' event
  yield f": connected client={client_id or 'anonymous'}\n\n".encode("utf-8")
  yield b"event: ready\ndata: {}\n\n"

  try:
    while True:
      await asyncio.sleep(15)
      # Comment frame is a valid SSE keep-alive
      yield b": keep-alive\n\n"
  except asyncio.CancelledError:
    # Let cancellation propagate without yielding further bytes
    raise


async def sse(request: Request) -> StreamingResponse:
  """SSE endpoint at /mcp/sse."""
  client_id = request.query_params.get("client_id")
  headers = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
  }
  return StreamingResponse(
    _sse_generator(client_id),
    media_type="text/event-stream",
    headers=headers,
  )


routes = [
  Route("/health", endpoint=health, methods=["GET"]),
  Route("/info", endpoint=info, methods=["GET"]),
  Route("/mcp/sse", endpoint=sse, methods=["GET"]),
]

# ASGI app for uvicorn
app = Starlette(routes=routes)