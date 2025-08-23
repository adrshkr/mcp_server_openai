"""
Response formatting utilities for API endpoints.

This module provides consistent response formatting and streaming capabilities.
"""

import json
from datetime import UTC, datetime
from typing import Any

from fastapi.responses import JSONResponse, StreamingResponse


class StreamingJSONResponse(JSONResponse):
    """Custom JSON response class with streaming capabilities."""

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: Any | None = None,
    ):
        # Ensure content is properly formatted
        if content is not None and not isinstance(content, dict):
            content = {"data": content}

        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


class ResponseFormatter:
    """Utility class for formatting API responses consistently."""

    @staticmethod
    def success_response(
        data: Any, message: str | None = None, status_code: int = 200, extra_fields: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a standardized success response."""

        response = {"status": "success", "data": data, "timestamp": datetime.now(UTC).isoformat()}

        if message:
            response["message"] = message

        if extra_fields:
            response.update(extra_fields)

        return response

    @staticmethod
    def error_response(
        error_code: str, error_message: str, details: dict[str, Any] | None = None, status_code: int = 500
    ) -> dict[str, Any]:
        """Create a standardized error response."""

        error_data = {"code": error_code, "message": error_message, "timestamp": datetime.now(UTC).isoformat()}

        if details:
            error_data["details"] = details

        return {"status": "error", "error": error_data}

    @staticmethod
    def health_response(
        status: str, uptime: float, checks: dict[str, Any], extra_info: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a standardized health check response."""

        response = {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": status,
            "uptime": uptime,
            "checks": checks,
        }

        if extra_info:
            response.update(extra_info)

        return response

    @staticmethod
    def info_response(
        service_name: str,
        version: str,
        endpoints: dict[str, Any],
        features: dict[str, bool],
        extra_info: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a standardized service info response."""

        response = {
            "service": service_name,
            "version": version,
            "timestamp": datetime.now(UTC).isoformat(),
            "endpoints": endpoints,
            "features": features,
        }

        if extra_info:
            response.update(extra_info)

        return response

    @staticmethod
    def content_generation_response(
        content_type: str,
        file_path: str,
        file_size: str,
        generation_time: float,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a standardized content generation response."""

        response = {
            "content_type": content_type,
            "file_path": file_path,
            "file_size": file_size,
            "generation_time": f"{generation_time:.2f}s",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if metadata:
            response["metadata"] = metadata

        return response

    @staticmethod
    def list_response(
        items: list,
        total_count: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        extra_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a standardized list response with pagination info."""

        response = {"items": items, "count": len(items), "timestamp": datetime.now(UTC).isoformat()}

        if total_count is not None:
            response["total_count"] = total_count

        if page is not None and page_size is not None:
            response["pagination"] = {
                "page": page,
                "page_size": page_size,
                "has_more": total_count is not None and (page * page_size) < total_count,
            }

        if extra_fields:
            response.update(extra_fields)

        return response


class StreamingResponseGenerator:
    """Generator for streaming responses with progress updates."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = datetime.now(UTC)

    async def generate_progress_stream(self, steps: list, operation_func):
        """Generate a streaming response with progress updates."""

        total_steps = len(steps)

        # Send initial response
        yield self._format_stream_message(
            {
                "type": "start",
                "operation": self.operation_name,
                "total_steps": total_steps,
                "timestamp": self.start_time.isoformat(),
            }
        )

        try:
            for i, step in enumerate(steps):
                # Send progress update
                yield self._format_stream_message(
                    {
                        "type": "progress",
                        "step": i + 1,
                        "total_steps": total_steps,
                        "current_step": step,
                        "progress_percent": round((i + 1) / total_steps * 100, 1),
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )

                # Execute step
                step_result = await operation_func(step)

                # Send step completion
                yield self._format_stream_message(
                    {
                        "type": "step_complete",
                        "step": i + 1,
                        "result": step_result,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )

            # Send completion
            end_time = datetime.now(UTC)
            duration = (end_time - self.start_time).total_seconds()

            yield self._format_stream_message(
                {
                    "type": "complete",
                    "operation": self.operation_name,
                    "duration": f"{duration:.2f}s",
                    "timestamp": end_time.isoformat(),
                }
            )

        except Exception as e:
            # Send error
            yield self._format_stream_message(
                {
                    "type": "error",
                    "operation": self.operation_name,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

    def _format_stream_message(self, data: dict[str, Any]) -> str:
        """Format a message for streaming."""
        return f"data: {json.dumps(data)}\n\n"


def create_streaming_response(generator) -> StreamingResponse:
    """Create a streaming response from a generator."""
    return StreamingResponse(
        generator,
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "Content-Type": "text/event-stream"},
    )
