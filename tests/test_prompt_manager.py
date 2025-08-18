import json

import pytest

from mcp_server_openai import config

# Skip the whole module if PromptManager isn't present yet.
try:
    from mcp_server_openai.prompts.manager import render  # type: ignore
except Exception:
    pytest.skip("PromptManager not implemented yet (Milestone 2.2).", allow_module_level=True)


def _set_env(monkeypatch: pytest.MonkeyPatch, cfg: dict) -> None:
    """
    Helper to inject config via MCP_CONFIG_JSON and clear YAML path + caches.
    """
    monkeypatch.delenv("MCP_CONFIG_PATH", raising=False)
    monkeypatch.setenv("MCP_CONFIG_JSON", json.dumps(cfg))
    config.load_config.cache_clear()


def test_render_defaults_no_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Renders summarize without client_id using defaults (or empty config).
    Asserts the template and baseline instructions are present.
    """
    _set_env(monkeypatch, cfg={})  # no defaults; template defaults must kick in

    out = render("summarize", params={"topic": "LLMs"}, client_id=None)
    assert isinstance(out, str)
    assert 'Summarize the topic "LLMs"' in out
    # The starter template includes these instruction lines:
    assert "Output format:" in out
    assert "Use plain text bullets" in out
    # Ensure we didn't accidentally render an empty string
    assert len(out.strip()) > 20


def test_render_with_client_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Provides per-client overrides via MCP_CONFIG_JSON and checks they appear in the
    rendered text.
    """
    cfg = {
        "prompts": {
            "summarize": {
                "defaults": {
                    "tone": "concise",
                    "audience": "general",
                    "bullets_min": 4,
                    "bullets_max": 6,
                },
                "clients": {
                    "acme": {
                        "tone": "detailed",
                        "audience": "executives",
                        "bullets_min": 5,
                        "bullets_max": 7,
                    }
                },
            }
        }
    }
    _set_env(monkeypatch, cfg=cfg)

    out = render("summarize", params={"topic": "LLMs"}, client_id="acme")
    assert 'Summarize the topic "LLMs"' in out
    # From client overrides:
    assert "executives" in out
    assert "detailed" in out
    # Bullet range 5–7 should surface somewhere in instructions
    assert "5" in out and "7" in out


def test_params_override_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    User-supplied params should take precedence over config defaults/overrides.
    """
    cfg = {
        "prompts": {
            "summarize": {
                "defaults": {"tone": "concise", "audience": "general"},
                "clients": {"demo": {"tone": "formal", "audience": "leaders"}},
            }
        }
    }
    _set_env(monkeypatch, cfg=cfg)

    # Pass tone override in params; it should win over defaults/clients.
    out = render("summarize", params={"topic": "RAG", "tone": "friendly"}, client_id="demo")
    assert 'Summarize the topic "RAG"' in out
    assert "friendly" in out
    # Ensure the losing values are not the only ones present
    assert "formal" not in out  # client override should NOT win over explicit param
    # Audience can still come from client/default since we didn't override it here
    assert "leaders" in out or "general" in out
