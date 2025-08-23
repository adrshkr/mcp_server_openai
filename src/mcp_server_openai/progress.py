from __future__ import annotations

import time
import uuid
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol

from . import logging_utils
from .notifications import get_notifier

_logger = logging_utils.get_logger("mcp.progress")


class ProgressListener(Protocol):
    """Protocol for progress event listeners."""

    def on_progress_update(self, event: ProgressEvent) -> None:
        """Handle progress update event."""
        ...


@dataclass
class ProgressEvent:
    """Progress event data structure."""

    progress_id: str
    tool_name: str
    request_id: str
    step_name: str
    progress_percent: float | None = None
    details: dict[str, Any] = field(default_factory=dict)
    elapsed_ms: float | None = None
    eta_ms: float | None = None
    parent_id: str | None = None
    correlation_id: str | None = None
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))


class ProgressTracker:
    """
    Modern progress tracker with advanced features:
    - Percentage tracking with ETA calculation
    - Hierarchical progress (parent/child relationships)
    - Real-time event publishing
    - Context manager support
    - Async/await support
    - Progress aggregation and rollup
    """

    def __init__(
        self,
        tool_name: str,
        request_id: str,
        total_steps: int | None = None,
        parent: ProgressTracker | None = None,
        correlation_id: str | None = None,
        listeners: list[ProgressListener] | None = None,
    ) -> None:
        self.progress_id = str(uuid.uuid4())
        self.tool_name = tool_name
        self.request_id = request_id
        self.total_steps = total_steps
        self.correlation_id = correlation_id or logging_utils.create_correlation_id()

        # Hierarchy
        self.parent = parent
        self.children: list[ProgressTracker] = []
        if parent:
            parent.children.append(self)

        # State tracking
        self.current_step = 0
        self.start_time = time.monotonic()
        self.step_times: list[float] = []
        self.current_step_name = ""
        self.is_completed = False
        self._last_progress_percent: float | None = None

        # Event system
        self.listeners = listeners or []

        # Add logging listener by default
        self.listeners.append(LoggingProgressListener())

    def add_listener(self, listener: ProgressListener) -> None:
        """Add a progress event listener."""
        self.listeners.append(listener)

    def remove_listener(self, listener: ProgressListener) -> None:
        """Remove a progress event listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def _emit_event(self, event: ProgressEvent) -> None:
        """Emit progress event to all listeners."""
        for listener in self.listeners:
            try:
                listener.on_progress_update(event)
            except Exception as e:
                # Don't let listener errors break progress tracking
                _logger.warning(f"Progress listener error: {e}")

    def step(
        self,
        name: str,
        details: dict[str, Any] | None = None,
        progress_percent: float | None = None,
    ) -> None:
        """Record a progress step."""
        if self.is_completed:
            return

        self.current_step += 1
        self.current_step_name = name
        current_time = time.monotonic()
        self.step_times.append(current_time)

        # Calculate progress percentage
        if progress_percent is None and self.total_steps:
            progress_percent = min(100.0, (self.current_step / self.total_steps) * 100.0)

        # Store last progress percentage for aggregation
        if progress_percent is not None:
            self._last_progress_percent = progress_percent

        # Calculate ETA
        eta_ms = None
        if progress_percent and progress_percent > 0 and progress_percent < 100:
            elapsed_ms = (current_time - self.start_time) * 1000
            remaining_percent = 100.0 - progress_percent
            eta_ms = (elapsed_ms / progress_percent) * remaining_percent

        event = ProgressEvent(
            progress_id=self.progress_id,
            tool_name=self.tool_name,
            request_id=self.request_id,
            step_name=name,
            progress_percent=progress_percent,
            details=details or {},
            elapsed_ms=(current_time - self.start_time) * 1000,
            eta_ms=eta_ms,
            parent_id=self.parent.progress_id if self.parent else None,
            correlation_id=self.correlation_id,
        )

        self._emit_event(event)

    def update_progress(
        self,
        progress_percent: float,
        step_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Update progress with explicit percentage."""
        if self.is_completed:
            return

        if not (0.0 <= progress_percent <= 100.0):
            raise ValueError("progress_percent must be between 0.0 and 100.0")

        if step_name:
            self.current_step_name = step_name

        current_time = time.monotonic()

        # Store last progress percentage for aggregation
        self._last_progress_percent = progress_percent

        # Calculate ETA
        eta_ms = None
        if progress_percent > 0 and progress_percent < 100:
            elapsed_ms = (current_time - self.start_time) * 1000
            remaining_percent = 100.0 - progress_percent
            eta_ms = (elapsed_ms / progress_percent) * remaining_percent

        event = ProgressEvent(
            progress_id=self.progress_id,
            tool_name=self.tool_name,
            request_id=self.request_id,
            step_name=step_name or self.current_step_name or "progress_update",
            progress_percent=progress_percent,
            details=details or {},
            elapsed_ms=(current_time - self.start_time) * 1000,
            eta_ms=eta_ms,
            parent_id=self.parent.progress_id if self.parent else None,
            correlation_id=self.correlation_id,
        )

        self._emit_event(event)

    def complete(
        self,
        final_step: str = "completed",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Mark progress as completed."""
        if self.is_completed:
            return

        self.is_completed = True
        self.current_step_name = final_step
        self._last_progress_percent = 100.0

        current_time = time.monotonic()

        event = ProgressEvent(
            progress_id=self.progress_id,
            tool_name=self.tool_name,
            request_id=self.request_id,
            step_name=final_step,
            progress_percent=100.0,
            details=details or {},
            elapsed_ms=(current_time - self.start_time) * 1000,
            eta_ms=0.0,
            parent_id=self.parent.progress_id if self.parent else None,
            correlation_id=self.correlation_id,
        )

        self._emit_event(event)

        # Send notification on completion
        notifier = get_notifier()
        if notifier:
            notifier.notify(
                title=f"Task Completed: {self.tool_name}",
                message=f"Tool '{self.tool_name}' finished successfully.",
            )

    def create_subtask(
        self,
        subtask_name: str,
        total_steps: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> ProgressTracker:
        """Create a child progress tracker for a subtask."""
        subtask = ProgressTracker(
            tool_name=f"{self.tool_name}.{subtask_name}",
            request_id=self.request_id,
            total_steps=total_steps,
            parent=self,
            correlation_id=self.correlation_id,
            listeners=self.listeners.copy(),  # Inherit listeners
        )
        return subtask

    def get_aggregated_progress(self) -> float:
        """Calculate aggregated progress including all children."""
        if not self.children:
            if self.total_steps and self.current_step:
                return min(100.0, (self.current_step / self.total_steps) * 100.0)
            return 0.0

        # For parents with children, calculate based on children's current progress
        total_progress = 0.0
        for child in self.children:
            # Use child's last reported progress percentage or calculate from steps
            if hasattr(child, "_last_progress_percent") and child._last_progress_percent is not None:
                total_progress += child._last_progress_percent
            else:
                total_progress += child.get_aggregated_progress()

        return total_progress / len(self.children) if self.children else 0.0

    @contextmanager
    def step_context(
        self,
        name: str,
        details: dict[str, Any] | None = None,
    ) -> Generator[None, None, None]:
        """Context manager for automatic step tracking."""
        try:
            self.step(name, details)
            yield
        except Exception as e:
            self.step(f"{name}_failed", {"error": str(e), **(details or {})})
            raise

    @asynccontextmanager
    async def async_step_context(
        self,
        name: str,
        details: dict[str, Any] | None = None,
    ) -> AsyncGenerator[None, None]:
        """Async context manager for automatic step tracking."""
        try:
            self.step(name, details)
            yield
        except Exception as e:
            self.step(f"{name}_failed", {"error": str(e), **(details or {})})
            raise


class LoggingProgressListener:
    """Default progress listener that logs to the standard logging system."""

    def on_progress_update(self, event: ProgressEvent) -> None:
        """Log progress event using the enhanced logging system."""
        logging_utils.log_progress(
            _logger,
            tool=event.tool_name,
            request_id=event.request_id,
            step=event.step_name,
            details={
                "progress_id": event.progress_id,
                "parent_id": event.parent_id,
                "elapsed_ms": event.elapsed_ms,
                "eta_ms": event.eta_ms,
                **event.details,
            },
            progress_percent=event.progress_percent,
            correlation_id=event.correlation_id,
        )


# Backwards compatibility alias
class Progress(ProgressTracker):
    """Backwards compatibility alias for ProgressTracker."""

    def __init__(self, tool_name: str, request_id: str) -> None:
        super().__init__(tool_name, request_id)

    def step(self, name: str, details: dict[str, Any] | None = None, progress_percent: float | None = None) -> None:
        """Backwards compatible step method."""
        super().step(name, details, progress_percent)


# Convenience factory functions
def create_progress_tracker(
    tool_name: str,
    request_id: str,
    total_steps: int | None = None,
    correlation_id: str | None = None,
) -> ProgressTracker:
    """Create a new progress tracker instance."""
    return ProgressTracker(
        tool_name=tool_name,
        request_id=request_id,
        total_steps=total_steps,
        correlation_id=correlation_id,
    )


def create_progress(
    tool_name: str,
    request_id: str,
) -> Progress:
    """Create a backwards-compatible Progress instance."""
    return Progress(tool_name, request_id)
