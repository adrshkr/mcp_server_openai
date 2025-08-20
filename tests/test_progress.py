import asyncio
import time
from unittest.mock import Mock

import pytest

from mcp_server_openai import progress


class TestProgressEvent:
    """Test cases for ProgressEvent data structure."""

    def test_progress_event_creation(self):
        """Test ProgressEvent creation with default values."""
        event = progress.ProgressEvent(
            progress_id="test-id",
            tool_name="test-tool",
            request_id="req-123",
            step_name="test-step",
        )

        assert event.progress_id == "test-id"
        assert event.tool_name == "test-tool"
        assert event.request_id == "req-123"
        assert event.step_name == "test-step"
        assert event.progress_percent is None
        assert event.details == {}
        assert event.elapsed_ms is None
        assert event.eta_ms is None
        assert event.parent_id is None
        assert event.correlation_id is None
        assert isinstance(event.timestamp_ms, int)

    def test_progress_event_with_all_fields(self):
        """Test ProgressEvent with all fields populated."""
        event = progress.ProgressEvent(
            progress_id="test-id",
            tool_name="test-tool",
            request_id="req-123",
            step_name="test-step",
            progress_percent=50.0,
            details={"key": "value"},
            elapsed_ms=1000.0,
            eta_ms=2000.0,
            parent_id="parent-id",
            correlation_id="corr-id",
        )

        assert event.progress_percent == 50.0
        assert event.details == {"key": "value"}
        assert event.elapsed_ms == 1000.0
        assert event.eta_ms == 2000.0
        assert event.parent_id == "parent-id"
        assert event.correlation_id == "corr-id"


class TestProgressTracker:
    """Test cases for ProgressTracker class."""

    def test_basic_progress_tracking(self):
        """Test basic progress tracking functionality."""
        mock_listener = Mock(spec=progress.ProgressListener)

        tracker = progress.ProgressTracker(
            tool_name="test-tool",
            request_id="req-123",
            total_steps=3,
            listeners=[mock_listener],
        )

        assert tracker.tool_name == "test-tool"
        assert tracker.request_id == "req-123"
        assert tracker.total_steps == 3
        assert tracker.current_step == 0
        assert not tracker.is_completed
        assert len(tracker.listeners) == 2  # Mock + LoggingProgressListener

        # Step 1
        tracker.step("step1", {"detail": "value1"})
        assert tracker.current_step == 1
        assert tracker.current_step_name == "step1"

        # Check that event was emitted
        assert mock_listener.on_progress_update.call_count == 1
        event = mock_listener.on_progress_update.call_args[0][0]
        assert event.step_name == "step1"
        assert event.progress_percent == pytest.approx(33.33, abs=0.01)
        assert event.details == {"detail": "value1"}

    def test_manual_progress_updates(self):
        """Test manual progress percentage updates."""
        mock_listener = Mock(spec=progress.ProgressListener)

        tracker = progress.ProgressTracker(
            tool_name="test-tool",
            request_id="req-123",
            listeners=[mock_listener],
        )

        tracker.update_progress(25.0, "quarter_done", {"stage": "processing"})

        assert mock_listener.on_progress_update.call_count == 1
        event = mock_listener.on_progress_update.call_args[0][0]
        assert event.progress_percent == 25.0
        assert event.step_name == "quarter_done"
        assert event.details == {"stage": "processing"}

    def test_progress_validation(self):
        """Test progress percentage validation."""
        tracker = progress.ProgressTracker("test-tool", "req-123")

        with pytest.raises(ValueError, match="progress_percent must be between 0.0 and 100.0"):
            tracker.update_progress(-10.0)

        with pytest.raises(ValueError, match="progress_percent must be between 0.0 and 100.0"):
            tracker.update_progress(150.0)

    def test_eta_calculation(self):
        """Test ETA calculation functionality."""
        mock_listener = Mock(spec=progress.ProgressListener)

        tracker = progress.ProgressTracker(
            tool_name="test-tool",
            request_id="req-123",
            listeners=[mock_listener],
        )

        # Sleep a bit to ensure meaningful elapsed time
        time.sleep(0.01)
        tracker.update_progress(25.0, "quarter_done")

        event = mock_listener.on_progress_update.call_args[0][0]
        assert event.elapsed_ms > 0
        assert event.eta_ms is not None
        assert event.eta_ms > 0

        # At 25% progress, ETA should be approximately 3x elapsed time
        expected_eta = event.elapsed_ms * 3
        assert event.eta_ms == pytest.approx(expected_eta, rel=0.1)

    def test_completion(self):
        """Test progress completion."""
        mock_listener = Mock(spec=progress.ProgressListener)

        tracker = progress.ProgressTracker(
            tool_name="test-tool",
            request_id="req-123",
            listeners=[mock_listener],
        )

        tracker.complete("all_done", {"result": "success"})

        assert tracker.is_completed
        assert tracker.current_step_name == "all_done"

        event = mock_listener.on_progress_update.call_args[0][0]
        assert event.step_name == "all_done"
        assert event.progress_percent == 100.0
        assert event.eta_ms == 0.0
        assert event.details == {"result": "success"}

        # Further operations should be ignored
        initial_call_count = mock_listener.on_progress_update.call_count
        tracker.step("ignored")
        tracker.update_progress(50.0)

        assert mock_listener.on_progress_update.call_count == initial_call_count

    def test_hierarchical_progress(self):
        """Test parent-child progress relationships."""
        mock_listener = Mock(spec=progress.ProgressListener)

        parent = progress.ProgressTracker(
            tool_name="parent-tool",
            request_id="req-123",
            listeners=[mock_listener],
        )

        child = parent.create_subtask("subtask", total_steps=2)

        assert child.parent == parent
        assert child in parent.children
        assert child.tool_name == "parent-tool.subtask"
        assert child.request_id == "req-123"
        assert child.correlation_id == parent.correlation_id

        child.step("child_step")

        # Both parent and child should have emitted events
        assert mock_listener.on_progress_update.call_count >= 1

        # Check that child event has parent_id
        child_events = [
            call.args[0]
            for call in mock_listener.on_progress_update.call_args_list
            if call.args[0].parent_id == parent.progress_id
        ]
        assert len(child_events) >= 1
        assert child_events[0].progress_id == child.progress_id

    def test_aggregated_progress(self):
        """Test aggregated progress calculation."""
        parent = progress.ProgressTracker("parent-tool", "req-123", total_steps=2)

        child1 = parent.create_subtask("subtask1")
        child2 = parent.create_subtask("subtask2")

        # Set child progress
        child1.update_progress(60.0)
        child2.update_progress(40.0)

        # Aggregated progress should be average of children
        aggregated = parent.get_aggregated_progress()
        assert aggregated == 50.0  # (60 + 40) / 2

    def test_step_context_manager(self):
        """Test step context manager functionality."""
        mock_listener = Mock(spec=progress.ProgressListener)

        tracker = progress.ProgressTracker(
            tool_name="test-tool",
            request_id="req-123",
            listeners=[mock_listener],
        )

        with tracker.step_context("test_step", {"context": "test"}):
            pass

        assert mock_listener.on_progress_update.call_count == 1
        event = mock_listener.on_progress_update.call_args[0][0]
        assert event.step_name == "test_step"
        assert event.details == {"context": "test"}

    def test_step_context_manager_with_exception(self):
        """Test step context manager with exception handling."""
        mock_listener = Mock(spec=progress.ProgressListener)

        tracker = progress.ProgressTracker(
            tool_name="test-tool",
            request_id="req-123",
            listeners=[mock_listener],
        )

        with pytest.raises(ValueError):
            with tracker.step_context("failing_step"):
                raise ValueError("Test error")

        assert mock_listener.on_progress_update.call_count == 2

        # First event should be the step start
        first_event = mock_listener.on_progress_update.call_args_list[0][0][0]
        assert first_event.step_name == "failing_step"

        # Second event should be the failure
        second_event = mock_listener.on_progress_update.call_args_list[1][0][0]
        assert second_event.step_name == "failing_step_failed"
        assert "error" in second_event.details

    def test_async_step_context_manager(self):
        """Test async step context manager functionality."""
        mock_listener = Mock(spec=progress.ProgressListener)

        tracker = progress.ProgressTracker(
            tool_name="test-tool",
            request_id="req-123",
            listeners=[mock_listener],
        )

        async def async_test():
            async with tracker.async_step_context("async_step", {"async": True}):
                await asyncio.sleep(0.001)  # Small async operation

        # Run the async test
        asyncio.run(async_test())

        assert mock_listener.on_progress_update.call_count == 1
        event = mock_listener.on_progress_update.call_args[0][0]
        assert event.step_name == "async_step"
        assert event.details == {"async": True}

    def test_listener_management(self):
        """Test progress listener management."""
        tracker = progress.ProgressTracker("test-tool", "req-123")
        initial_count = len(tracker.listeners)

        mock_listener = Mock(spec=progress.ProgressListener)
        tracker.add_listener(mock_listener)
        assert len(tracker.listeners) == initial_count + 1

        tracker.remove_listener(mock_listener)
        assert len(tracker.listeners) == initial_count

    def test_listener_error_handling(self):
        """Test that listener errors don't break progress tracking."""
        failing_listener = Mock(spec=progress.ProgressListener)
        failing_listener.on_progress_update.side_effect = Exception("Listener error")

        tracker = progress.ProgressTracker(
            tool_name="test-tool",
            request_id="req-123",
            listeners=[failing_listener],
        )

        # This should not raise an exception
        tracker.step("test_step")

        # Verify the failing listener was called
        assert failing_listener.on_progress_update.call_count == 1


class TestLoggingProgressListener:
    """Test cases for LoggingProgressListener."""

    def test_logging_progress_listener(self):
        """Test that LoggingProgressListener logs correctly."""
        # Test that the listener works without throwing exceptions
        listener = progress.LoggingProgressListener()

        event = progress.ProgressEvent(
            progress_id="test-id",
            tool_name="test-tool",
            request_id="req-123",
            step_name="test_step",
            progress_percent=50.0,
            details={"detail": "value"},
        )

        # This should not raise any exceptions
        listener.on_progress_update(event)

        # Test with a tracker that uses the listener
        tracker = progress.ProgressTracker("test-tool", "req-123")
        tracker.step("test_step", {"detail": "value"}, 50.0)

        # If we get here without exceptions, the logging worked


class TestBackwardsCompatibility:
    """Test backwards compatibility with the old Progress class."""

    def test_progress_class_compatibility(self):
        """Test that the old Progress class interface still works."""
        prog = progress.Progress("test-tool", "req-123")
        prog.step("test_step", {"detail": "value"})

        # Verify the Progress class has the expected attributes
        assert prog.tool_name == "test-tool"
        assert prog.request_id == "req-123"
        assert prog.current_step_name == "test_step"
        assert prog.current_step >= 1

    def test_factory_functions(self):
        """Test convenience factory functions."""
        tracker = progress.create_progress_tracker("test-tool", "req-123", 5)
        assert isinstance(tracker, progress.ProgressTracker)
        assert tracker.tool_name == "test-tool"
        assert tracker.total_steps == 5

        compat_progress = progress.create_progress("test-tool", "req-123")
        assert isinstance(compat_progress, progress.Progress)
        assert compat_progress.tool_name == "test-tool"


class TestProgressIntegration:
    """Integration tests for progress tracking."""

    def test_complex_workflow(self):
        """Test a complex workflow with hierarchical progress."""
        main_tracker = progress.ProgressTracker("main-task", "req-123", total_steps=3)

        # Step 1: Initialization
        with main_tracker.step_context("initialization"):
            time.sleep(0.01)

        # Step 2: Processing with subtasks
        with main_tracker.step_context("processing"):
            subtask1 = main_tracker.create_subtask("data_loading", total_steps=2)
            subtask1.step("load_config")
            subtask1.step("load_data")
            subtask1.complete("data_loaded")

            subtask2 = main_tracker.create_subtask("data_processing")
            subtask2.update_progress(30.0, "validating")
            subtask2.update_progress(60.0, "transforming")
            subtask2.update_progress(100.0, "complete")

        # Step 3: Finalization
        main_tracker.step("finalization")
        main_tracker.complete("all_done", {"result": "success"})

        # Verify the workflow completed correctly
        assert main_tracker.is_completed
        assert main_tracker.current_step_name == "all_done"
        assert len(main_tracker.children) == 2

        # Verify subtasks
        assert subtask1.is_completed
        assert subtask1.current_step_name == "data_loaded"
        assert subtask2._last_progress_percent == 100.0
