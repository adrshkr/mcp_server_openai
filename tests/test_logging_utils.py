import json
import logging
import threading
from unittest.mock import patch

import pytest

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


class TestJsonFormatter:
    """Test cases for JsonFormatter class."""

    def test_basic_message_formatting(self, caplog):
        """Test basic string message formatting."""
        formatter = logging_utils.JsonFormatter()
        logger = logging.getLogger("test")
        logger.addHandler(logging.StreamHandler())
        logger.handlers[0].setFormatter(formatter)

        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="Test message", args=(), exc_info=None
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["message"] == "Test message"
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert "timestamp" in data

    def test_dict_message_formatting(self):
        """Test dictionary message formatting."""
        formatter = logging_utils.JsonFormatter(sanitize_sensitive=False)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg={"event": "test", "data": {"key": "value"}},
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["event"] == "test"
        assert data["data"] == {"key": "value"}

    def test_json_string_message_formatting(self):
        """Test JSON string message formatting."""
        formatter = logging_utils.JsonFormatter()

        json_msg = json.dumps({"parsed": True, "value": 42})
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg=json_msg, args=(), exc_info=None
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["parsed"] is True
        assert data["value"] == 42

    def test_sensitive_data_sanitization(self):
        """Test that sensitive data is properly sanitized."""
        formatter = logging_utils.JsonFormatter(sanitize_sensitive=True)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg={"password": "secret123", "api_key": "key123", "data": "safe"},
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["password"] == "[REDACTED]"
        assert data["api_key"] == "[REDACTED]"
        assert data["data"] == "safe"

    def test_thread_safety(self):
        """Test that formatter is thread-safe."""
        formatter = logging_utils.JsonFormatter()
        results = []

        def log_message(msg):
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0, msg=msg, args=(), exc_info=None
            )
            result = formatter.format(record)
            results.append(json.loads(result))

        threads = []
        for i in range(10):
            thread = threading.Thread(target=log_message, args=(f"message_{i}",))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 10
        messages = [r["message"] for r in results]
        assert len(set(messages)) == 10  # All unique

    def test_exception_formatting(self):
        """Test exception information formatting."""
        formatter = logging_utils.JsonFormatter()

        try:
            raise ValueError("Test error")
        except ValueError as e:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Error occurred",
                args=(),
                exc_info=(type(e), e, e.__traceback__),
            )

        result = formatter.format(record)
        data = json.loads(result)

        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"
        assert data["exception"]["message"] == "Test error"
        assert "traceback" in data["exception"]

    def test_fallback_on_serialization_error(self):
        """Test fallback when JSON serialization fails."""
        formatter = logging_utils.JsonFormatter()

        # Create object that can't be serialized
        class NonSerializable:
            pass

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg={"obj": NonSerializable()},
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["error_type"] == "json_serialization_failed"
        assert "Log formatting error" in data["message"]


class TestLoggingHelpers:
    """Test cases for logging helper functions."""

    def test_log_accept(self, capsys):
        """Test log_accept function."""
        logger = logging_utils.get_logger("test.accept")

        logging_utils.log_accept(
            logger,
            tool="test_tool",
            request_id="req_123",
            client_id="client_456",
            payload={"data": "value"},
            correlation_id="corr_789",
        )

        captured = capsys.readouterr()
        objs = _json_lines(captured.err)
        assert len(objs) >= 1

        log_entry = objs[0]
        assert log_entry["event_type"] == "request_accepted"
        assert log_entry["tool"] == "test_tool"
        assert log_entry["request_id"] == "req_123"
        assert log_entry["client_id"] == "client_456"
        assert log_entry["payload"] == {"data": "value"}
        assert log_entry["correlation_id"] == "corr_789"
        assert "timestamp_ms" in log_entry

    def test_log_accept_validation(self):
        """Test log_accept parameter validation."""
        logger = logging_utils.get_logger("test.validation")

        with pytest.raises(ValueError, match="tool and request_id are required"):
            logging_utils.log_accept(logger, tool="", request_id="req_123")

        with pytest.raises(ValueError, match="tool and request_id are required"):
            logging_utils.log_accept(logger, tool="test_tool", request_id="")

    def test_log_progress(self, capsys):
        """Test log_progress function."""
        logger = logging_utils.get_logger("test.progress")

        logging_utils.log_progress(
            logger,
            tool="test_tool",
            request_id="req_123",
            step="processing",
            details={"stage": "validation"},
            progress_percent=25.5,
            correlation_id="corr_789",
        )

        captured = capsys.readouterr()
        objs = _json_lines(captured.err)
        assert len(objs) >= 1

        log_entry = objs[0]
        assert log_entry["event_type"] == "progress_update"
        assert log_entry["step"] == "processing"
        assert log_entry["details"] == {"stage": "validation"}
        assert log_entry["progress_percent"] == 25.5

    def test_log_progress_validation(self):
        """Test log_progress parameter validation."""
        logger = logging_utils.get_logger("test.validation")

        with pytest.raises(ValueError, match="progress_percent must be between 0.0 and 100.0"):
            logging_utils.log_progress(logger, tool="test", request_id="req", step="step", progress_percent=150.0)

        with pytest.raises(ValueError, match="progress_percent must be between 0.0 and 100.0"):
            logging_utils.log_progress(logger, tool="test", request_id="req", step="step", progress_percent=-10.0)

    def test_log_response(self, capsys):
        """Test log_response function."""
        logger = logging_utils.get_logger("test.response")

        logging_utils.log_response(
            logger,
            tool="test_tool",
            request_id="req_123",
            status="success",
            duration_ms=123.45,
            response_size=1024,
            status_code=200,
            metadata={"cache_hit": True},
        )

        captured = capsys.readouterr()
        objs = _json_lines(captured.err)
        assert len(objs) >= 1

        log_entry = objs[0]
        assert log_entry["event_type"] == "request_completed"
        assert log_entry["status"] == "success"
        assert log_entry["duration_ms"] == 123.45
        assert log_entry["response_size_bytes"] == 1024
        assert log_entry["status_code"] == 200
        assert log_entry["metadata"] == {"cache_hit": True}

    def test_log_response_validation(self):
        """Test log_response parameter validation."""
        logger = logging_utils.get_logger("test.validation")

        with pytest.raises(ValueError, match="duration_ms cannot be negative"):
            logging_utils.log_response(logger, tool="test", request_id="req", duration_ms=-1.0)

        with pytest.raises(ValueError, match="response_size cannot be negative"):
            logging_utils.log_response(logger, tool="test", request_id="req", response_size=-100)

    def test_log_exception(self, capsys):
        """Test log_exception function."""
        logger = logging_utils.get_logger("test.exception")

        exc = ValueError("Test error")
        exc.custom_attr = "custom_value"

        logging_utils.log_exception(
            logger,
            tool="test_tool",
            request_id="req_123",
            exc=exc,
            correlation_id="corr_789",
            context={"operation": "data_validation"},
            recoverable=True,
        )

        captured = capsys.readouterr()
        objs = _json_lines(captured.err)
        assert len(objs) >= 1

        log_entry = objs[0]
        assert log_entry["event_type"] == "error_occurred"
        assert log_entry["error_type"] == "ValueError"
        assert log_entry["error_message"] == "Test error"
        assert log_entry["recoverable"] is True
        assert log_entry["correlation_id"] == "corr_789"
        assert log_entry["context"] == {"operation": "data_validation"}
        assert log_entry["error_attributes"] == {"custom_attr": "custom_value"}

    def test_log_performance_metric(self, capsys):
        """Test log_performance_metric function."""
        logger = logging_utils.get_logger("test.metrics")

        logging_utils.log_performance_metric(
            logger,
            metric_name="response_time",
            value=123.45,
            unit="ms",
            tool="test_tool",
            request_id="req_123",
            tags={"region": "us-west", "version": "1.0"},
        )

        captured = capsys.readouterr()
        objs = _json_lines(captured.err)
        assert len(objs) >= 1

        log_entry = objs[0]
        assert log_entry["event_type"] == "performance_metric"
        assert log_entry["metric_name"] == "response_time"
        assert log_entry["value"] == 123.45
        assert log_entry["unit"] == "ms"
        assert log_entry["tags"] == {"region": "us-west", "version": "1.0"}


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_create_correlation_id(self):
        """Test correlation ID generation."""
        id1 = logging_utils.create_correlation_id()
        id2 = logging_utils.create_correlation_id()

        assert id1 != id2
        assert isinstance(id1, str)
        assert len(id1) == 36  # UUID4 length

    def test_get_logger_configuration(self):
        """Test logger configuration options."""
        logger = logging_utils.get_logger(
            "test.config", level="DEBUG", propagate=True, formatter_config={"include_thread_info": False}
        )

        assert logger.level == logging.DEBUG
        assert logger.propagate is True
        assert isinstance(logger.handlers[0].formatter, logging_utils.JsonFormatter)

    def test_get_logger_validation(self):
        """Test logger parameter validation."""
        with pytest.raises(ValueError, match="Logger name cannot be empty"):
            logging_utils.get_logger("")

    @patch("logging.config.dictConfig")
    def test_configure_logging(self, mock_dict_config):
        """Test application-wide logging configuration."""
        logging_utils.configure_logging(
            level="DEBUG", format_config={"sanitize_sensitive": False}, disable_existing_loggers=True
        )

        mock_dict_config.assert_called_once()
        config = mock_dict_config.call_args[0][0]

        assert config["disable_existing_loggers"] is True
        assert config["root"]["level"] == "DEBUG"
        assert config["formatters"]["json"]["sanitize_sensitive"] is False


def test_backwards_compatibility(capsys):
    """Test backwards compatibility with existing usage patterns."""
    logger = logging_utils.get_logger("test.compat")

    # Test old-style calls still work
    logging_utils.log_accept(logger, tool="t", request_id="r", client_id="c", payload={"data": 1})
    logging_utils.log_progress(logger, tool="t", request_id="r", step="s", details={"x": "y"})
    logging_utils.log_response(logger, tool="t", request_id="r", status="ok", duration_ms=12.3, size=7)
    logging_utils.log_exception(logger, tool="t", request_id="r", exc=ValueError("boom"))

    captured = capsys.readouterr()
    objs = _json_lines(captured.err)
    assert len(objs) >= 4

    # Verify event types are properly set
    event_types = [obj.get("event_type") for obj in objs]
    assert "request_accepted" in event_types
    assert "progress_update" in event_types
    assert "request_completed" in event_types
    assert "error_occurred" in event_types


@pytest.fixture
def isolated_logger():
    """Provide an isolated logger for testing."""
    import uuid

    logger_name = f"test_{uuid.uuid4().hex[:8]}"
    yield logging_utils.get_logger(logger_name)
    # Cleanup
    logger = logging.getLogger(logger_name)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
