import json
import logging
import threading
import time
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    """
    Thread-safe JSON formatter for structured logging.

    Features:
    - Structured JSON output with consistent schema
    - Thread-safe operation with local state
    - Sensitive data sanitization
    - High-precision timestamps
    - Graceful error handling
    """

    _SENSITIVE_KEYS = frozenset(
        {
            "password",
            "token",
            "secret",
            "key",
            "authorization",
            "api_key",
            "access_token",
            "refresh_token",
            "credential",
        }
    )

    def __init__(self, include_thread_info: bool = True, sanitize_sensitive: bool = True) -> None:
        super().__init__()
        self.include_thread_info = include_thread_info
        self.sanitize_sensitive = sanitize_sensitive
        self._lock = threading.Lock()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON with thread safety."""
        with self._lock:
            return self._format_record(record)

    def _format_record(self, record: logging.LogRecord) -> str:
        """Internal record formatting logic."""
        # Base log object with high-precision timestamp
        log_obj: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add thread information if enabled
        if self.include_thread_info:
            log_obj.update(
                {
                    "thread_id": record.thread,
                    "thread_name": record.threadName,
                    "process_id": record.process,
                }
            )

        # Process message content
        self._process_message(record, log_obj)

        # Add exception information if present
        if record.exc_info:
            log_obj["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Sanitize sensitive data
        if self.sanitize_sensitive:
            log_obj = self._sanitize_data(log_obj)

        try:
            return json.dumps(log_obj, ensure_ascii=False, separators=(",", ":"))
        except (TypeError, ValueError) as e:
            # Fallback for non-serializable objects
            return self._create_fallback_log(record, str(e))

    def _process_message(self, record: logging.LogRecord, log_obj: dict[str, Any]) -> None:
        """Process and merge message content into log object."""
        msg_obj = record.msg
        merged = False

        # Case 1: Dict message - merge directly
        if isinstance(msg_obj, dict):
            log_obj.update(msg_obj)
            merged = True
        # Case 2: Try parsing as JSON string
        elif isinstance(msg_obj, str) and msg_obj.strip().startswith(("{", "[")):
            try:
                parsed = json.loads(record.getMessage())
                if isinstance(parsed, dict):
                    log_obj.update(parsed)
                    merged = True
                else:
                    log_obj["data"] = parsed
                    merged = True
            except (json.JSONDecodeError, ValueError):
                # Not valid JSON, treat as string message
                pass

        # Case 3: Regular string message
        if not merged:
            log_obj["message"] = record.getMessage()

    def _sanitize_data(self, data: Any) -> Any:
        """Recursively sanitize sensitive information from log data."""
        if isinstance(data, dict):
            return {
                k: "[REDACTED]" if k.lower() in self._SENSITIVE_KEYS else self._sanitize_data(v)
                for k, v in data.items()
            }
        elif isinstance(data, list | tuple):
            return [self._sanitize_data(item) for item in data]
        return data

    def _create_fallback_log(self, record: logging.LogRecord, error: str) -> str:
        """Create fallback log entry when JSON serialization fails."""
        fallback = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": f"Log formatting error: {error}",
            "original_message": str(record.msg),
            "error_type": "json_serialization_failed",
        }
        return json.dumps(fallback, ensure_ascii=False, separators=(",", ":"), default=str)


def _ensure_json_formatter(logger: logging.Logger, formatter_config: dict[str, Any] | None = None) -> None:
    """
    Ensure all handlers on this logger use JsonFormatter with given configuration.
    If there are no handlers, attach a StreamHandler with JsonFormatter.

    Args:
        logger: The logger instance to configure
        formatter_config: Optional configuration for JsonFormatter
    """
    config = formatter_config or {}

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter(**config))
        logger.addHandler(handler)
    else:
        for handler in logger.handlers:  # type: ignore[assignment]
            # Only update if not already a JsonFormatter
            if not isinstance(handler.formatter, JsonFormatter):
                handler.setFormatter(JsonFormatter(**config))


def get_logger(
    name: str,
    level: int | str = logging.INFO,
    propagate: bool = False,
    formatter_config: dict[str, Any] | None = None,
) -> logging.Logger:
    """
    Return a logger configured with JsonFormatter.

    Args:
        name: Logger name (typically module name)
        level: Logging level (default: INFO)
        propagate: Whether to propagate to parent loggers (default: False)
        formatter_config: Optional JsonFormatter configuration

    Returns:
        Configured logger instance
    """
    if not name:
        raise ValueError("Logger name cannot be empty")

    logger = logging.getLogger(name)
    _ensure_json_formatter(logger, formatter_config)

    # Set level if it's a string
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    logger.setLevel(level)
    logger.propagate = propagate
    return logger


def log_accept(
    logger: logging.Logger,
    *,
    tool: str,
    request_id: str,
    client_id: str | None = None,
    payload: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> None:
    """
    Log request acceptance event.

    Args:
        logger: Logger instance
        tool: Tool name being invoked
        request_id: Unique request identifier
        client_id: Optional client identifier
        payload: Request payload (will be sanitized)
        correlation_id: Optional correlation ID for tracing
    """
    if not tool or not request_id:
        raise ValueError("tool and request_id are required")

    log_data = {
        "event_type": "request_accepted",
        "tool": tool,
        "request_id": request_id,
        "timestamp_ms": int(time.time() * 1000),
    }

    if client_id:
        log_data["client_id"] = client_id
    if payload:
        log_data["payload"] = payload
    if correlation_id:
        log_data["correlation_id"] = correlation_id

    logger.info(log_data)


def log_progress(
    logger: logging.Logger,
    *,
    tool: str,
    request_id: str,
    step: str,
    details: dict[str, Any] | None = None,
    progress_percent: float | None = None,
    correlation_id: str | None = None,
) -> None:
    """
    Log progress update event.

    Args:
        logger: Logger instance
        tool: Tool name being executed
        request_id: Unique request identifier
        step: Current processing step
        details: Optional step details
        progress_percent: Optional progress percentage (0.0-100.0)
        correlation_id: Optional correlation ID for tracing
    """
    if not tool or not request_id or not step:
        raise ValueError("tool, request_id, and step are required")

    if progress_percent is not None and not (0.0 <= progress_percent <= 100.0):
        raise ValueError("progress_percent must be between 0.0 and 100.0")

    log_data = {
        "event_type": "progress_update",
        "tool": tool,
        "request_id": request_id,
        "step": step,
        "timestamp_ms": int(time.time() * 1000),
    }

    if details:
        log_data["details"] = details
    if progress_percent is not None:
        log_data["progress_percent"] = progress_percent
    if correlation_id:
        log_data["correlation_id"] = correlation_id

    logger.info(log_data)


def log_response(
    logger: logging.Logger,
    *,
    tool: str,
    request_id: str,
    status: str = "success",
    duration_ms: float | None = None,
    response_size: int | None = None,
    status_code: int | None = None,
    correlation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    # Backwards compatibility
    size: int | None = None,
) -> None:
    """
    Log response completion event.

    Args:
        logger: Logger instance
        tool: Tool name that was executed
        request_id: Unique request identifier
        status: Response status (success, error, timeout, etc.)
        duration_ms: Execution duration in milliseconds
        response_size: Response size in bytes
        status_code: HTTP-like status code
        correlation_id: Optional correlation ID for tracing
        metadata: Additional response metadata
        size: DEPRECATED - use response_size instead
    """
    if not tool or not request_id:
        raise ValueError("tool and request_id are required")

    if duration_ms is not None and duration_ms < 0:
        raise ValueError("duration_ms cannot be negative")

    # Handle backwards compatibility
    actual_size = response_size if response_size is not None else size
    if actual_size is not None and actual_size < 0:
        raise ValueError("response_size cannot be negative")

    # Support old status values
    if status == "ok":
        status = "success"

    log_data = {
        "event_type": "request_completed",
        "tool": tool,
        "request_id": request_id,
        "status": status,
        "timestamp_ms": int(time.time() * 1000),
    }

    if duration_ms is not None:
        log_data["duration_ms"] = round(duration_ms, 3)
    if actual_size is not None:
        log_data["response_size_bytes"] = actual_size
    if status_code is not None:
        log_data["status_code"] = status_code
    if correlation_id:
        log_data["correlation_id"] = correlation_id
    if metadata:
        log_data["metadata"] = metadata

    logger.info(log_data)


def log_exception(
    logger: logging.Logger,
    *,
    tool: str,
    request_id: str,
    exc: Exception,
    correlation_id: str | None = None,
    context: dict[str, Any] | None = None,
    recoverable: bool = False,
) -> None:
    """
    Log exception event with detailed error information.

    Args:
        logger: Logger instance
        tool: Tool name where exception occurred
        request_id: Unique request identifier
        exc: Exception instance
        correlation_id: Optional correlation ID for tracing
        context: Additional context about the error
        recoverable: Whether the error is recoverable
    """
    if not tool or not request_id or not exc:
        raise ValueError("tool, request_id, and exc are required")

    log_data = {
        "event_type": "error_occurred",
        "tool": tool,
        "request_id": request_id,
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
        "recoverable": recoverable,
        "timestamp_ms": int(time.time() * 1000),
    }

    if correlation_id:
        log_data["correlation_id"] = correlation_id
    if context:
        log_data["context"] = context

    # Add exception attributes if available
    if hasattr(exc, "__dict__"):
        exc_attrs = {
            k: v for k, v in exc.__dict__.items() if not k.startswith("_") and isinstance(v, str | int | float | bool)
        }
        if exc_attrs:
            log_data["error_attributes"] = exc_attrs

    logger.error(log_data, exc_info=exc)


def create_correlation_id() -> str:
    """
    Generate a unique correlation ID for request tracing.

    Returns:
        Unique correlation identifier
    """
    import uuid

    return str(uuid.uuid4())


def log_performance_metric(
    logger: logging.Logger,
    *,
    metric_name: str,
    value: int | float,
    unit: str,
    tool: str | None = None,
    request_id: str | None = None,
    tags: dict[str, str] | None = None,
) -> None:
    """
    Log performance metrics for monitoring and alerting.

    Args:
        logger: Logger instance
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement (ms, bytes, count, etc.)
        tool: Optional tool name
        request_id: Optional request identifier
        tags: Optional metric tags
    """
    if not metric_name:
        raise ValueError("metric_name is required")

    log_data: dict[str, Any] = {
        "event_type": "performance_metric",
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "timestamp_ms": int(time.time() * 1000),
    }

    if tool:
        log_data["tool"] = tool
    if request_id:
        log_data["request_id"] = request_id
    if tags:
        log_data["tags"] = tags

    logger.info(log_data)


def configure_logging(
    level: int | str = logging.INFO,
    format_config: dict[str, Any] | None = None,
    disable_existing_loggers: bool = False,
) -> None:
    """
    Configure application-wide logging with structured JSON format.

    Args:
        level: Default logging level
        format_config: JsonFormatter configuration
        disable_existing_loggers: Whether to disable existing loggers
    """
    config = {
        "version": 1,
        "disable_existing_loggers": disable_existing_loggers,
        "formatters": {"json": {"()": JsonFormatter, **(format_config or {})}},
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json", "level": level}},
        "root": {"level": level, "handlers": ["console"]},
    }

    import logging.config

    logging.config.dictConfig(config)
