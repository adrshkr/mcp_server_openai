"""
Enhanced Error Handling and Monitoring for Streamable HTTP Server.

Provides comprehensive error handling, monitoring, and observability features
for the modern streamable HTTP server implementation.
"""

from __future__ import annotations

import asyncio
import functools
import traceback
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from .logging_utils import get_logger

_logger = get_logger("mcp.error_handling")

# Global error tracking
_error_stats: dict[str, Any] = {
    "total_errors": 0,
    "error_types": {},
    "last_error": None,
    "error_rate_window": [],
}


class EnhancedHTTPException(HTTPException):
    """Enhanced HTTP exception with additional context."""

    def __init__(
        self,
        status_code: int,
        detail: str = "",
        headers: dict[str, str] | None = None,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ):
        super().__init__(status_code, detail, headers)
        self.error_code = error_code
        self.context = context or {}
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.now(UTC)


class ErrorHandler:
    """Centralized error handling with monitoring and recovery."""

    def __init__(self) -> None:
        self.error_callbacks: dict[type[Exception], Callable] = {}
        self.recovery_strategies: dict[type[Exception], Callable] = {}

    def register_error_callback(self, error_type: type[Exception], callback: Callable) -> None:
        """Register a callback for specific error types."""
        self.error_callbacks[error_type] = callback

    def register_recovery_strategy(self, error_type: type[Exception], strategy: Callable) -> None:
        """Register a recovery strategy for specific error types."""
        self.recovery_strategies[error_type] = strategy

    async def handle_error(
        self, request: Request, error: Exception, context: dict[str, Any] | None = None
    ) -> JSONResponse:
        """Handle errors with comprehensive logging and monitoring."""
        error_id = str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        # Track error statistics
        _error_stats["total_errors"] += 1
        error_type_name = type(error).__name__
        _error_stats["error_types"][error_type_name] = _error_stats["error_types"].get(error_type_name, 0) + 1
        _error_stats["last_error"] = {
            "error_id": error_id,
            "type": error_type_name,
            "message": str(error),
            "timestamp": datetime.now(UTC).isoformat(),
            "path": str(request.url),
            "method": request.method,
        }

        # Log error with full context
        error_context = {
            "error_id": error_id,
            "correlation_id": correlation_id,
            "request_path": str(request.url),
            "request_method": request.method,
            "user_agent": request.headers.get("User-Agent"),
            "client_ip": request.client.host if request.client else None,
            "error_type": error_type_name,
            "traceback": traceback.format_exc(),
            **(context or {}),
        }

        _logger.error(f"Request error: {error}", extra=error_context)

        # Execute error callback if registered
        error_type = type(error)
        if error_type in self.error_callbacks:
            try:
                await self.error_callbacks[error_type](request, error, error_context)
            except Exception as callback_error:
                _logger.error(f"Error callback failed: {callback_error}")

        # Attempt recovery if strategy is registered
        if error_type in self.recovery_strategies:
            try:
                recovery_result = await self.recovery_strategies[error_type](request, error, error_context)
                if recovery_result:
                    _logger.info(f"Error recovery successful for {error_id}")
                    # Type check: ensure recovery_result is a JSONResponse
                    if isinstance(recovery_result, JSONResponse):
                        return recovery_result
                    else:
                        _logger.warning(f"Recovery strategy returned non-JSONResponse: {type(recovery_result)}")
            except Exception as recovery_error:
                _logger.error(f"Error recovery failed: {recovery_error}")

        # Determine response based on error type
        if isinstance(error, EnhancedHTTPException):
            status_code = error.status_code
            error_detail = error.detail
            error_code = error.error_code
        elif isinstance(error, HTTPException):
            status_code = error.status_code
            error_detail = error.detail
            error_code = None
        else:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            error_detail = "Internal server error"
            error_code = "INTERNAL_ERROR"

        # Create error response
        error_response: dict[str, Any] = {
            "error": {
                "error_id": error_id,
                "error_code": error_code,
                "message": error_detail,
                "timestamp": datetime.now(UTC).isoformat(),
                "path": str(request.url),
                "correlation_id": correlation_id,
            }
        }

        # Add debug information in development
        if _logger.level <= 10:  # DEBUG level
            error_response["error"]["debug"] = {
                "type": error_type_name,
                "traceback": traceback.format_exc().split("\n"),
            }

        headers = {
            "X-Error-ID": error_id,
            "X-Correlation-ID": correlation_id,
            "Content-Type": "application/json",
        }

        return JSONResponse(error_response, status_code=status_code, headers=headers)


# Global error handler instance
error_handler = ErrorHandler()


def error_boundary(
    fallback_response: Response | None = None,
    error_types: tuple[type[Exception], ...] | None = None,
    log_errors: bool = True,
    raise_on_error: bool = False,
) -> Callable[[Callable], Callable]:
    """Decorator for creating error boundaries around functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                if error_types and not isinstance(e, error_types):
                    raise

                if log_errors:
                    _logger.error(f"Error in {func.__name__}: {e}", exc_info=True)

                if raise_on_error:
                    raise

                if fallback_response:
                    return fallback_response

                # Return a generic error response
                return JSONResponse(
                    {"error": {"message": "An unexpected error occurred", "function": func.__name__}}, status_code=500
                )

        return wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise EnhancedHTTPException(
                    503,
                    "Service temporarily unavailable",
                    error_code="CIRCUIT_BREAKER_OPEN",
                    context={"failure_count": self.failure_count, "state": self.state},
                )

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Success - reset circuit breaker
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                _logger.info("Circuit breaker reset to CLOSED state")

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now(UTC)

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                _logger.warning(f"Circuit breaker opened after {self.failure_count} failures", extra={"error": str(e)})

            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True
        return (datetime.now(UTC) - self.last_failure_time).total_seconds() > self.recovery_timeout


class RetryHandler:
    """Retry logic with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        retryable_exceptions: tuple = (Exception,),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retryable_exceptions = retryable_exceptions

    async def retry(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with retry logic."""
        last_exception: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except self.retryable_exceptions as e:
                last_exception = e

                if attempt == self.max_retries:
                    _logger.error(f"All retry attempts failed for {func.__name__}: {e}")
                    raise

                delay = min(self.base_delay * (self.backoff_factor**attempt), self.max_delay)
                _logger.warning(f"Retry attempt {attempt + 1} for {func.__name__} after {delay}s delay: {e}")
                await asyncio.sleep(delay)

        if last_exception is not None:
            raise last_exception
        else:
            raise RuntimeError("Retry failed but no exception was captured")


class HealthMonitor:
    """Monitor system health and performance."""

    def __init__(self) -> None:
        self.health_checks: dict[str, Callable] = {}
        self.health_status: dict[str, Any] = {"status": "healthy", "checks": {}, "last_update": None}

    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function."""
        self.health_checks[name] = check_func

    async def run_health_checks(self) -> dict[str, Any]:
        """Run all health checks and return status."""
        checks = {}
        overall_healthy = True

        for name, check_func in self.health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()

                checks[name] = {"status": "healthy", "result": result, "timestamp": datetime.now(UTC).isoformat()}
            except Exception as e:
                checks[name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                overall_healthy = False

        self.health_status = {
            "status": "healthy" if overall_healthy else "unhealthy",
            "checks": checks,
            "last_update": datetime.now(UTC).isoformat(),
        }

        return self.health_status

    def get_health_status(self) -> dict[str, Any]:
        """Get current health status."""
        return self.health_status


# Global instances
circuit_breaker = CircuitBreaker()
retry_handler = RetryHandler()
health_monitor = HealthMonitor()


# Exception handlers for Starlette
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return await error_handler.handle_error(request, exc)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    return await error_handler.handle_error(request, exc)


# Register default health checks
def database_health_check() -> dict[str, Any]:
    """Check database connectivity."""
    # TODO: Implement actual database check
    return {"connection": "ok", "query_time_ms": 1.2}


def memory_health_check() -> dict[str, Any]:
    """Check memory usage."""
    import psutil

    memory = psutil.virtual_memory()
    return {"usage_percent": memory.percent, "available_gb": round(memory.available / (1024**3), 2)}


def disk_health_check() -> dict[str, Any]:
    """Check disk space."""
    import psutil

    disk = psutil.disk_usage("/")
    return {"usage_percent": (disk.used / disk.total) * 100, "free_gb": round(disk.free / (1024**3), 2)}


# Register default health checks
health_monitor.register_health_check("memory", memory_health_check)
health_monitor.register_health_check("disk", disk_health_check)


def get_error_stats() -> dict[str, Any]:
    """Get current error statistics."""
    return _error_stats.copy()
