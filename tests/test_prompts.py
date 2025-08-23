from mcp_server_openai.prompts.summarize import summarize_prompt


def test_summarize_prompt_default() -> None:
    assert summarize_prompt("Python") == "Please provide a concise summary of the topic: Python."


def test_summarize_prompt_custom_tone() -> None:
    assert (
        summarize_prompt("Databases", tone="detailed") == "Please provide a detailed summary of the topic: Databases."
    )
