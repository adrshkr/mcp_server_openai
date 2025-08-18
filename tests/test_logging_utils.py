import json
import logging

from mcp_server_openai import logging_utils


def _json_lines(stderr_text: str) -> list[dict]:
    """
    Extract JSON objects from stderr (one JSON object per line).
    Filters out any non-JSON lines (e.g., blank lines or prefixes).
    """
    out: list[dict] = []
    for ln in stderr_text.splitlines():
        s = ln.strip()
        if not s or not s.startswith("{"):
            continue
        try:
            out.append(json.loads(s))
        except Exception:
            # ignore any non-JSON noise
            pass
    return out


def test_json_formatter_and_helpers(capsys) -> None:
    logger = logging_utils.get_logger("test.logger")
    logger.setLevel(logging.INFO)

    logging_utils.log_accept(logger, tool="t", client_id="c", request_id="r", payload={"k": 1})
    logging_utils.log_progress(logger, tool="t", request_id="r", step="s", details={"x": "y"})
    logging_utils.log_response(logger, tool="t", request_id="r", status="ok", duration_ms=12.3, size=7)
    logging_utils.log_exception(logger, tool="t", request_id="r", exc=ValueError("boom"))

    captured = capsys.readouterr()
    objs = _json_lines(captured.err)
    # We expect at least the four JSON lines we emitted
    assert len(objs) >= 4

    # Build an index by event type for easy assertions
    by_event = {o.get("event"): o for o in objs if "event" in o}

    assert "accept" in by_event
    assert by_event["accept"]["tool"] == "t"
    assert by_event["accept"]["request_id"] == "r"
    assert by_event["accept"]["client_id"] == "c"
    assert by_event["accept"]["payload"] == {"k": 1}

    assert "progress" in by_event
    assert by_event["progress"]["step"] == "s"
    assert by_event["progress"]["details"] == {"x": "y"}

    assert "response" in by_event
    assert by_event["response"]["status"] == "ok"
    assert "duration_ms" in by_event["response"]
    assert "size" in by_event["response"]

    assert "exception" in by_event
    assert by_event["exception"]["error"] == "boom"
