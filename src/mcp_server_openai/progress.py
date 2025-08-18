from typing import Any

from . import logging_utils

_logger = logging_utils.get_logger("mcp.progress")


class Progress:
    """
    Minimal progress helper.
    For now, just logs progress events; can be extended to publish to an event bus.
    """

    def __init__(self, tool_name: str, request_id: str) -> None:
        self._tool_name = tool_name
        self._request_id = request_id

    def step(self, name: str, details: dict[str, Any] | None = None) -> None:
        logging_utils.log_progress(
            _logger,
            tool=self._tool_name,
            request_id=self._request_id,
            step=name,
            details=details or {},
        )
