from mcp_server_openai.resources import health


def test_ping() -> None:
    assert health.ping() == "ok"
