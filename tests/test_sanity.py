from importlib import import_module


def test_import_and_run():
    """Tests that the main module can be imported and the hello function works."""
    try:
        mod = import_module("mcp_server_openai.main")
    except ImportError as e:
        raise ImportError("Failed to import the main package: mcp_server_openai.main") from e

    assert hasattr(mod, "hello"), "The 'hello' function is missing from main.py"
    assert mod.hello("gemini") == "Hello, gemini!"
