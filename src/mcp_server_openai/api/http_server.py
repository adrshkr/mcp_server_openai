from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, StreamingResponse
from starlette.routing import Route

from .health import health_checker


async def health(_: Request) -> PlainTextResponse:
    """Simple liveness check."""
    return PlainTextResponse("ok")


async def liveness(_: Request) -> JSONResponse:
    """Liveness probe for Cloud Run - determines if container should be restarted."""
    result = await health_checker.liveness_check()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(result, status_code=status_code)


async def readiness(_: Request) -> JSONResponse:
    """Readiness probe for Cloud Run - determines if container can accept traffic."""
    result = await health_checker.readiness_check()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(result, status_code=status_code)


async def startup(_: Request) -> JSONResponse:
    """Startup probe for Cloud Run - comprehensive startup health check."""
    result = await health_checker.startup_check()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(result, status_code=status_code)


async def status(_: Request) -> JSONResponse:
    """Detailed status information for monitoring and debugging."""
    result = await health_checker.detailed_status()
    return JSONResponse(result)


async def info(_: Request) -> JSONResponse:
    """Basic server info and advertised endpoints."""
    data: dict[str, Any] = {
        "name": "mcp_server_openai",
        "version": "0.2.0",
        "env": {"python": None},
        "endpoints": {
            "health": "/health",
            "liveness": "/health/live",
            "readiness": "/health/ready",
            "startup": "/health/startup",
            "status": "/status",
            "info": "/info",
            "mcp_sse": "/mcp/sse",
        },
        "notes": "Comprehensive health monitoring for GCP Cloud Run deployment. SSE endpoint with keep-alives.",
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
    yield f": connected client={client_id or 'anonymous'}\n\n".encode()
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
    # Basic health endpoint (legacy)
    Route("/health", endpoint=health, methods=["GET"]),
    # GCP Cloud Run health probes
    Route("/health/live", endpoint=liveness, methods=["GET"]),
    Route("/health/ready", endpoint=readiness, methods=["GET"]),
    Route("/health/startup", endpoint=startup, methods=["GET"]),
    # Detailed monitoring
    Route("/status", endpoint=status, methods=["GET"]),
    Route("/info", endpoint=info, methods=["GET"]),
    # MCP SSE endpoint
    Route("/mcp/sse", endpoint=sse, methods=["GET"]),
]

# ASGI app for uvicorn
app = Starlette(routes=routes)
