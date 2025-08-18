import json
import logging
from typing import Any


class JsonFormatter(logging.Formatter):
    """
    Format records as single-line JSON.

    Behavior:
    - If record.msg is a dict, merge it into the top-level JSON object.
    - Else, try json.loads(record.getMessage()); if it yields a dict, merge that.
    - Else, include the formatted message under "msg".
    - Include "exc_info" text when present.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
        }

        merged = False
        msg_obj: Any = record.msg

        # Case 1: logging.info({...})
        if isinstance(msg_obj, dict):
            log_obj.update(msg_obj)
            merged = True
        else:
            # Case 2: maybe a pre-serialized JSON string
            try:
                parsed = json.loads(record.getMessage())
                if isinstance(parsed, dict):
                    log_obj.update(parsed)
                    merged = True
            except Exception:
                # Not JSON; fall through
                pass

        if not merged:
            # Plain string (possibly with %-formatting applied already)
            log_obj["msg"] = record.getMessage()

        if record.exc_info:
            # Attach formatted traceback (single line JSON string)
            log_obj["exc_info"] = self.formatException(record.exc_info)

        # Single-line JSON
        return json.dumps(log_obj, ensure_ascii=False)


def _ensure_json_formatter(logger: logging.Logger) -> None:
    """
    Ensure all handlers on this logger use JsonFormatter.
    If there are no handlers, attach a StreamHandler with JsonFormatter.
    """
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    else:
        for h in logger.handlers:
            # Always enforce our formatter to satisfy tests
            h.setFormatter(JsonFormatter())


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger configured with JsonFormatter and INFO level.
    Non-propagating to avoid duplicate logs in tests.
    """
    logger = logging.getLogger(name)
    _ensure_json_formatter(logger)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def log_accept(
    logger: logging.Logger,
    *,
    tool: str,
    client_id: str | None,
    request_id: str,
    payload: dict,
) -> None:
    logger.info(
        {
            "event": "accept",
            "tool": tool,
            "request_id": request_id,
            "client_id": client_id,
            "payload": payload,
        }
    )


def log_progress(
    logger: logging.Logger,
    *,
    tool: str,
    request_id: str,
    step: str,
    details: dict | None = None,
) -> None:
    logger.info(
        {
            "event": "progress",
            "tool": tool,
            "request_id": request_id,
            "step": step,
            "details": details or {},
        }
    )


def log_response(
    logger: logging.Logger,
    *,
    tool: str,
    request_id: str,
    status: str = "ok",
    duration_ms: float | None = None,
    size: int | None = None,
) -> None:
    data: dict[str, Any] = {
        "event": "response",
        "tool": tool,
        "request_id": request_id,
        "status": status,
    }
    if duration_ms is not None:
        data["duration_ms"] = duration_ms
    if size is not None:
        data["size"] = size
    logger.info(data)


def log_exception(
    logger: logging.Logger,
    *,
    tool: str,
    request_id: str,
    exc: Exception,
) -> None:
    logger.error(
        {
            "event": "exception",
            "tool": tool,
            "request_id": request_id,
            "error": str(exc),
        },
        exc_info=exc,
    )
