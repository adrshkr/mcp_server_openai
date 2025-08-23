"""
CLI entrypoint.

Usage:
  uv run python -m mcp_server_openai --stdio
  uv run python -m mcp_server_openai --http --host 0.0.0.0 --port 8000

If installed (pip install -e .), you can also run:
  uv run mcp_server_openai --http
"""

from __future__ import annotations

import argparse

from mcp_server_openai.server import app as stdio_app


def main() -> None:
    ap = argparse.ArgumentParser(prog="mcp_server_openai")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--stdio", action="store_true", help="Run MCP over stdio (dev).")
    mode.add_argument("--http", action="store_true", help="Run HTTP server (Starlette/Uvicorn).")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    if args.http:
        import uvicorn

        from mcp_server_openai.http_server import app as http_app

        uvicorn.run(http_app, host=args.host, port=args.port)
    else:
        # default: stdio for dev
        stdio_app.run()


if __name__ == "__main__":
    main()
