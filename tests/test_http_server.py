from starlette.testclient import TestClient

from mcp_server_openai.http_server import app


def test_health():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.text == "ok"


def test_info():
    with TestClient(app) as client:
        r = client.get("/info")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "mcp_server_openai"
        assert "/mcp/sse" in data["endpoints"]["mcp_sse"]
