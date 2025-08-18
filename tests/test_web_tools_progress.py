import asyncio
import json
import logging
import sys  # Add this import

import httpx
import pytest

from mcp_server_openai.logging_utils import JsonFormatter, get_logger
from mcp_server_openai.tools import web_tools

# ---------- Test doubles (no real network) ----------


class _DummyResp:
    def __init__(self, body: str) -> None:
        self.status_code = 200
        self._text = body
        self.headers = {"server": "dummy", "content-type": "text/plain"}
        self.elapsed = 0.0  # keep simple & stable

    @property
    def text(self) -> str:  # mimic httpx.Response.text
        return self._text

    def raise_for_status(self) -> None:
        return None


class _DummyAsyncClient:
    def __init__(self, body: str) -> None:
        self._body = body

    async def __aenter__(self) -> "_DummyAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        return None

    async def get(self, url: str, timeout: int | float | None = None, follow_redirects: bool = True) -> _DummyResp:
        # return a minimal response object the helper expects
        return _DummyResp(self._body)

    async def aclose(self) -> None:
        return None


# ---------- Helpers to parse JSON lines from stderr ----------
# Ensure _json_lines and _first_event are correct
def _json_lines(s: str) -> list[dict]:
    """Parse multiple JSON objects from stderr output."""
    lines = [line.strip() for line in s.splitlines() if line.strip()]
    parsed = []
    for line in lines:
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return parsed


def _first_event(objs, event_name):
    if not objs:
        return None
    for obj in objs:
        event = obj.get("event")
        if event == event_name:
            return obj
    print(f"Available events: {[obj.get('event') for obj in objs]}")  # Debug print
    return None


# ---------- Tests ---------
def test_fetch_url_logging_and_progress(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    # Stub AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: _DummyAsyncClient("ok"))

    # Get logger with JsonFormatter
    web_logger = get_logger("mcp.tool.web.fetch_url")

    # Ensure stderr handler with JsonFormatter
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    web_logger.handlers = [handler]
    web_logger.setLevel(logging.INFO)
    web_logger.propagate = False

    # Clear existing output
    capsys.readouterr()

    # Run the fetch
    res = asyncio.run(web_tools.fetch_url_content("example.com/test path"))

    # Flush handler
    handler.flush()

    # Capture output
    captured = capsys.readouterr()

    # Parse logs (keep it simple)
    objs = [json.loads(line) for line in captured.err.splitlines() if line.strip()]

    # Get all events for debugging
    events = [obj.get("event") for obj in objs]
    print(f"Found events: {events}")

    # Check required events (single assertion block)
    assert "progress" in events, f"missing 'progress' event\nEvents: {events}\nstderr:\n{captured.err}"
    assert "response" in events, f"missing 'response' event\nEvents: {events}\nstderr:\n{captured.err}"
    assert "accept" in events, f"missing 'accept' event\nEvents: {events}\nstderr:\n{captured.err}"

    # Verify response data
    assert res.url.startswith("https://example.com/test%20path")
    assert res.status_code == 200
    assert res.headers.get("server") == "dummy"
    assert res.content_preview.startswith("ok:https://example.com/test%20path")

    # Verify flattened result
    flat = web_tools.flatten_fetch_result(res)
    assert isinstance(flat, dict)
    assert isinstance(flat["status_code"], int)
    assert isinstance(flat["truncated"], bool)
    assert flat["error"] is None
    hdrs = json.loads(flat["headers_json"])
    assert hdrs["server"] == "dummy"

    # Check for required log events
    progress = _first_event(objs, "progress")
    response = _first_event(objs, "response")
    assert progress is not None, f"missing 'progress' event log\nstderr:\n{captured.err}"
    assert response is not None, f"missing 'response' event log\nstderr:\n{captured.err}"

    # If 'accept' is present, verify its tool name
    accept = _first_event(objs, "accept")
    if accept is not None:
        assert accept.get("tool") == "web.fetch_url"
