"""
Standardized logging system for MCP Server OpenAI.

Provides consistent logging patterns, structured context, and centralized configuration.
"""

import logging
import logging.config
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class StandardLogger:
    """Standardized logger with structured context support."""

    def __init__(self, name: str, component: str | None = None):
        self.logger = logging.getLogger(f"mcp.{name}")
        self.component = component or name

    def _add_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Add standard context to log entries."""
        return {"component": self.component, "timestamp": datetime.now(UTC).isoformat(), **context}

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with context."""
        self.logger.debug(message, extra=self._add_context(context))

    def info(self, message: str, **context: Any) -> None:
        """Log info message with context."""
        self.logger.info(message, extra=self._add_context(context))

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with context."""
        self.logger.warning(message, extra=self._add_context(context))

    def error(self, message: str, error: Exception | None = None, **context: Any) -> None:
        """Log error message with context and optional exception."""
        extra_context = self._add_context(context)
        if error:
            extra_context["error_type"] = type(error).__name__
            extra_context["error_message"] = str(error)

        self.logger.error(message, extra=extra_context, exc_info=error is not None)

    def critical(self, message: str, error: Exception | None = None, **context: Any) -> None:
        """Log critical message with context and optional exception."""
        extra_context = self._add_context(context)
        if error:
            extra_context["error_type"] = type(error).__name__
            extra_context["error_message"] = str(error)

        self.logger.critical(message, extra=extra_context, exc_info=error is not None)

    def log_request(self, method: str, path: str, status_code: int, duration: float, **context: Any) -> None:
        """Log HTTP request with standard format."""
        self.info(
            f"{method} {path} - {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration * 1000, 2),
            **context,
        )

    def log_operation(self, operation: str, success: bool, duration: float | None = None, **context: Any) -> None:
        """Log operation result with standard format."""
        status = "SUCCESS" if success else "FAILED"
        message = f"Operation {operation}: {status}"

        log_context = {"operation": operation, "success": success, **context}

        if duration is not None:
            log_context["duration_ms"] = round(duration * 1000, 2)

        if success:
            self.info(message, **log_context)
        else:
            self.error(message, **log_context)


def setup_logging(
    level: str | int = logging.INFO,
    log_file: Path | None = None,
    json_format: bool = False,
    include_console: bool = True,
) -> None:
    """Setup standardized logging configuration."""

    # Create logs directory if needed
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(component)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {},
        "loggers": {
            "mcp": {"level": level, "handlers": [], "propagate": False},
            "uvicorn": {"level": "INFO", "handlers": [], "propagate": False},
            "fastapi": {"level": "INFO", "handlers": [], "propagate": False},
        },
    }

    # Add console handler
    if include_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "detailed",
            "stream": sys.stdout,
        }
        config["loggers"]["mcp"]["handlers"].append("console")
        config["loggers"]["uvicorn"]["handlers"].append("console")
        config["loggers"]["fastapi"]["handlers"].append("console")

    # Add file handler
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "detailed",
            "filename": str(log_file),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
        }
        config["loggers"]["mcp"]["handlers"].append("file")
        config["loggers"]["uvicorn"]["handlers"].append("file")
        config["loggers"]["fastapi"]["handlers"].append("file")

    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str, component: str | None = None) -> StandardLogger:
    """Get a standardized logger instance."""
    return StandardLogger(name, component)


# Default logger setup
_default_setup_done = False


def ensure_default_logging() -> None:
    """Ensure default logging is set up."""
    global _default_setup_done
    if not _default_setup_done:
        setup_logging(level=logging.INFO, log_file=Path("logs/mcp_server.log"), include_console=True)
        _default_setup_done = True


# Additional utility functions for compatibility
def create_correlation_id() -> str:
    """Create a unique correlation ID for request tracking."""
    import uuid

    return str(uuid.uuid4())


def log_progress(
    logger: StandardLogger,
    tool: str,
    request_id: str,
    step: str,
    details: dict[str, Any] | None = None,
    progress_percent: float | None = None,
    correlation_id: str | None = None,
) -> None:
    """Log progress information with structured context."""
    context = {
        "tool": tool,
        "request_id": request_id,
        "step": step,
        "correlation_id": correlation_id,
        **(details or {}),
    }

    if progress_percent is not None:
        context["progress_percent"] = progress_percent

    logger.info(f"Progress: {tool} - {step}", **context)


# Auto-setup default logging
ensure_default_logging()
