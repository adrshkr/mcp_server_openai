from mcp_server_openai.config import get_prompt_vars


def test_get_prompt_vars_merge(monkeypatch):
    yaml_text = """
prompts:
  summarize:
    defaults:
      tone: concise
    clients:
      acme:
        tone: detailed
"""
    # write a temp config file
    import os
    import tempfile
    import textwrap

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
        f.write(textwrap.dedent(yaml_text))
        cfg_path = f.name

    try:
        monkeypatch.setenv("MCP_CONFIG_PATH", cfg_path)
        v_default = get_prompt_vars("summarize", None)
        v_acme = get_prompt_vars("summarize", "acme")
        assert v_default.get("tone") == "concise"
        assert v_acme.get("tone") == "detailed"
    finally:
        os.unlink(cfg_path)
