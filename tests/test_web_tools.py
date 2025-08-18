import asyncio
import json

from mcp_server_openai.tools import web_tools


class _DummyResponse:
    def __init__(self, text: str, status_code: int = 200, headers=None, url="https://example.com") -> None:
        self.text = text
        self.status_code = status_code
        self.headers = headers or {"content-type": "text/plain", "server": "dummy"}
        self.url = url
        self.elapsed = None  # mimic httpx attr

    def raise_for_status(self) -> None:
        pass  # not used in current implementation


class _DummyClient:
    def __init__(self, text: str, status: int = 200, headers=None) -> None:
        self._text = text
        self._status = status
        self._headers = headers or {"content-type": "text/plain", "server": "dummy"}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, url: str):
        return _DummyResponse(f"ok:{url}", self._status, self._headers, url=url)


def test_fetch_url_content_and_tool_flatten(monkeypatch) -> None:
    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: _DummyClient("ok"))

    # test helper
    res = asyncio.run(web_tools.fetch_url_content("example.com/test path"))
    assert res.url.startswith("https://example.com/test%20path")
    assert res.status_code == 200
    assert res.headers.get("server") == "dummy"
    assert res.content_preview.startswith("ok:https://example.com/test%20path")

    # test flattening logic (mirrors tool output)
    out = web_tools.flatten_fetch_result(res)
    assert isinstance(out, dict)
    assert isinstance(out["status_code"], int)
    assert isinstance(out["truncated"], bool)
    assert out["error"] is None

    hdrs = json.loads(out["headers_json"])
    assert hdrs.get("server") == "dummy"
