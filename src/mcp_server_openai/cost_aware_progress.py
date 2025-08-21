"""
Cost-aware progress tracking that integrates Claude usage monitoring
with the existing progress tracking system.
"""

from __future__ import annotations

from typing import Any

from .monitoring import EnhancedUsageTracker, get_monitoring_config
from .progress import ProgressTracker, create_progress_tracker


class CostAwareProgressTracker(ProgressTracker):
    """Enhanced progress tracker with Claude API cost tracking."""

    def __init__(self, tool_name: str, request_id: str, usage_tracker: EnhancedUsageTracker | None = None, **kwargs):
        super().__init__(tool_name, request_id, **kwargs)
        self.usage_tracker = usage_tracker
        self.token_usage = {"input": 0, "output": 0, "cost": 0.0, "requests": 0}
        self._monitoring_config = get_monitoring_config()

    async def track_api_call(
        self, input_tokens: int, output_tokens: int, cost: float, step_name: str | None = None
    ) -> None:
        """Track a Claude API call with cost and token usage."""
        # Update local tracking
        self.token_usage["input"] += input_tokens
        self.token_usage["output"] += output_tokens
        self.token_usage["cost"] += cost
        self.token_usage["requests"] += 1

        # Update global usage tracker if available
        if self.usage_tracker:
            await self.usage_tracker.track_api_call(input_tokens, output_tokens, cost)

        # Log the API call as a progress step
        step_name = step_name or f"api_call_{self.token_usage['requests']}"
        self.step(
            step_name,
            {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": cost,
                "cumulative_cost": self.token_usage["cost"],
                "cumulative_tokens": self.token_usage["input"] + self.token_usage["output"],
                "event_type": "api_call_tracked",
            },
        )

    def get_cost_summary(self) -> dict[str, Any]:
        """Get summary of costs incurred during this operation."""
        total_tokens = self.token_usage["input"] + self.token_usage["output"]
        return {
            "total_cost_usd": round(self.token_usage["cost"], 4),
            "total_tokens": total_tokens,
            "input_tokens": self.token_usage["input"],
            "output_tokens": self.token_usage["output"],
            "api_requests": self.token_usage["requests"],
            "avg_cost_per_request": round(self.token_usage["cost"] / max(self.token_usage["requests"], 1), 4),
            "avg_tokens_per_request": round(total_tokens / max(self.token_usage["requests"], 1), 2),
            "cost_per_token": round(self.token_usage["cost"] / max(total_tokens, 1), 6),
        }

    async def check_budget_status(self) -> dict[str, Any]:
        """Check current budget status and warnings."""
        if not self.usage_tracker or not self._monitoring_config.enabled:
            return {"status": "monitoring_disabled"}

        # Get current usage
        current_usage = await self.usage_tracker.get_current_usage()

        # Check limits
        limit_check = await self.usage_tracker.check_usage_limits(
            hourly_limit=self._monitoring_config.cost_limits.hourly_max,
            daily_limit=self._monitoring_config.cost_limits.daily_max,
        )

        return {
            "within_limits": limit_check["within_limits"],
            "warnings": limit_check["warnings"],
            "current_hourly_burn": current_usage.burn_rate_per_hour,
            "current_daily_burn": current_usage.burn_rate_per_day,
            "operation_cost": self.token_usage["cost"],
            "operation_tokens": self.token_usage["input"] + self.token_usage["output"],
        }

    def complete(self, final_step: str, details: dict[str, Any] | None = None) -> None:
        """Complete progress tracking with cost summary."""
        final_details = details or {}
        final_details.update(
            {"cost_summary": self.get_cost_summary(), "monitoring_enabled": self._monitoring_config.enabled}
        )
        super().complete(final_step, final_details)


def create_cost_aware_progress_tracker(
    tool_name: str, request_id: str, usage_tracker: EnhancedUsageTracker | None = None, **kwargs
) -> CostAwareProgressTracker:
    """Create a cost-aware progress tracker."""
    return CostAwareProgressTracker(tool_name=tool_name, request_id=request_id, usage_tracker=usage_tracker, **kwargs)


# Backwards compatible function that returns cost-aware tracker when monitoring is enabled
def create_progress_tracker_with_cost_monitoring(
    tool_name: str, request_id: str, usage_tracker: EnhancedUsageTracker | None = None, **kwargs
) -> ProgressTracker | CostAwareProgressTracker:
    """
    Create a progress tracker with optional cost monitoring.

    Returns CostAwareProgressTracker if monitoring is enabled,
    otherwise returns standard ProgressTracker for backwards compatibility.
    """
    config = get_monitoring_config()

    if config.enabled and usage_tracker:
        return CostAwareProgressTracker(
            tool_name=tool_name, request_id=request_id, usage_tracker=usage_tracker, **kwargs
        )
    else:
        # Fall back to standard progress tracker
        return create_progress_tracker(tool_name, request_id, **kwargs)
