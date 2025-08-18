def test_cli_import_main():
    import mcp_server_openai.__main__ as m

    assert callable(getattr(m, "main", None))
