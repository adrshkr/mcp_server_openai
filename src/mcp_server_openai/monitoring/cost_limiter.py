"""
Cost-aware rate limiting for Claude API usage with enhanced token tracking.

Provides dynamic rate limiting based on API costs and usage patterns
to prevent runaway expenses and ensure budget compliance.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from starlette.exceptions import HTTPException
from starlette.requests import Request

from ..logging_utils import get_logger
from .usage_tracker import EnhancedUsageTracker, UsageStats

_logger = get_logger("mcp.monitoring.limiter")


@dataclass
class CostLimits:
    """Cost limiting configuration with enhanced tracking."""

    hourly_max: float = 10.0
    daily_max: float = 100.0
    monthly_max: float = 1000.0
    per_request_max: float = 1.0
    tokens_per_hour_max: int = 100000
    warning_threshold: float = 0.8  # Warn at 80% of limit
    critical_threshold: float = 0.95  # Critical at 95% of limit


class CostAwareLimiter:
    """Enhanced rate limiter that considers API costs, tokens, and usage patterns."""

    def __init__(
        self, usage_tracker: EnhancedUsageTracker, cost_limits: CostLimits | None = None, enabled: bool = True
    ):
        self.usage_tracker = usage_tracker
        self.cost_limits = cost_limits or CostLimits()
        self.enabled = enabled
        self._client_usage: dict[str, dict[str, Any]] = {}
        self._last_cleanup = time.time()

    async def check_limits(self, request: Request) -> dict[str, Any]:
        """Check if request is within cost and token limits."""
        if not self.enabled:
            return {"allowed": True, "reason": "limiter_disabled"}

        client_id = self._get_client_id(request)
        current_usage = await self.usage_tracker.get_current_usage()

        # Check global limits
        global_check = await self._check_global_limits(current_usage)
        if not global_check["allowed"]:
            return global_check

        # Check per-client limits
        client_check = await self._check_client_limits(client_id, current_usage)
        if not client_check["allowed"]:
            return client_check

        # Update client usage tracking
        self._update_client_usage(client_id)

        return {
            "allowed": True,
            "reason": "within_limits",
            "usage_stats": current_usage.to_dict(),
            "warnings": current_usage.warnings,
            "inline_summary": current_usage.get_inline_summary(),
        }

    async def enforce_limits(self, request: Request) -> None:
        """Enforce cost limits, raising HTTPException if exceeded."""
        result = await self.check_limits(request)

        if not result["allowed"]:
            error_detail = {
                "error": "cost_limit_exceeded",
                "reason": result["reason"],
                "message": result.get("message", "API cost limits exceeded"),
                "usage_stats": result.get("usage_stats"),
                "retry_after": result.get("retry_after", 3600),  # 1 hour default
            }

            _logger.warning(
                "Cost limit exceeded",
                extra={
                    "client_id": self._get_client_id(request),
                    "reason": result["reason"],
                    "event_type": "cost_limit_exceeded",
                },
            )

            raise HTTPException(status_code=429, detail=error_detail.get("message", "API cost limits exceeded"))

        # Log warnings if approaching limits
        if result.get("warnings"):
            _logger.warning(
                "Usage approaching limits",
                extra={
                    "client_id": self._get_client_id(request),
                    "warnings": result["warnings"],
                    "event_type": "usage_warning",
                },
            )

    async def _check_global_limits(self, usage_stats: UsageStats) -> dict[str, Any]:
        """Check global cost and token limits."""
        # Check hourly cost limit
        if usage_stats.burn_rate_per_hour > self.cost_limits.hourly_max:
            return {
                "allowed": False,
                "reason": "hourly_cost_limit_exceeded",
                "message": f"Hourly cost limit of ${self.cost_limits.hourly_max:.2f} exceeded",
                "usage_stats": usage_stats.to_dict(),
                "retry_after": 3600,  # 1 hour
            }

        # Check daily cost limit
        if usage_stats.burn_rate_per_day > self.cost_limits.daily_max:
            return {
                "allowed": False,
                "reason": "daily_cost_limit_exceeded",
                "message": f"Daily cost limit of ${self.cost_limits.daily_max:.2f} exceeded",
                "usage_stats": usage_stats.to_dict(),
                "retry_after": 86400,  # 24 hours
            }

        # Check token rate limits
        hourly_token_rate = usage_stats.tokens.total_tokens / max(usage_stats.session_duration_minutes / 60.0, 1.0)
        if hourly_token_rate > self.cost_limits.tokens_per_hour_max:
            return {
                "allowed": False,
                "reason": "hourly_token_limit_exceeded",
                "message": f"Hourly token limit of {self.cost_limits.tokens_per_hour_max:,} exceeded",
                "usage_stats": usage_stats.to_dict(),
                "retry_after": 3600,
            }

        return {"allowed": True}

    async def _check_client_limits(self, client_id: str, usage_stats: UsageStats) -> dict[str, Any]:
        """Check per-client cost limits."""
        client_data = self._client_usage.get(client_id, {})
        cost_this_hour = client_data.get("cost_this_hour", 0.0)

        # Estimate cost per request
        avg_cost = usage_stats.avg_cost_per_request
        if avg_cost > self.cost_limits.per_request_max:
            return {
                "allowed": False,
                "reason": "per_request_limit_exceeded",
                "message": f"Request cost ${avg_cost:.4f} exceeds limit ${self.cost_limits.per_request_max:.4f}",
                "retry_after": 300,  # 5 minutes
            }

        # Check client hourly spending
        client_hourly_limit = self.cost_limits.hourly_max * 0.1  # 10% per client max
        if cost_this_hour > client_hourly_limit:
            return {
                "allowed": False,
                "reason": "client_hourly_limit_exceeded",
                "message": f"Client hourly limit of ${client_hourly_limit:.2f} exceeded",
                "retry_after": 3600,
            }

        return {"allowed": True}

    def _get_client_id(self, request: Request) -> str:
        """Extract client ID from request."""
        # Try various sources for client ID
        client_id = (
            request.query_params.get("client_id")
            or request.headers.get("X-Client-ID")
            or request.headers.get("User-Agent", "unknown")[:50]
            or str(request.client.host if request.client else "unknown")
        )
        return client_id

    def _update_client_usage(self, client_id: str) -> None:
        """Update client usage tracking."""
        now = time.time()
        hour_start = int(now // 3600) * 3600

        if client_id not in self._client_usage:
            self._client_usage[client_id] = {}

        client_data = self._client_usage[client_id]

        # Reset hourly counters if new hour
        if client_data.get("hour_start", 0) != hour_start:
            client_data.update({"hour_start": hour_start, "requests_this_hour": 0, "cost_this_hour": 0.0})

        # Increment counters
        client_data["requests_this_hour"] += 1
        client_data["last_request"] = now

        # Cleanup old client data periodically
        if now - self._last_cleanup > 3600:  # Every hour
            self._cleanup_old_clients()
            self._last_cleanup = now

    def _cleanup_old_clients(self) -> None:
        """Remove old client usage data."""
        now = time.time()
        cutoff = now - 86400  # Keep data for 24 hours

        to_remove = [
            client_id for client_id, data in self._client_usage.items() if data.get("last_request", 0) < cutoff
        ]

        for client_id in to_remove:
            del self._client_usage[client_id]

        if to_remove:
            _logger.info(f"Cleaned up {len(to_remove)} old client usage records")

    def get_client_stats(self) -> dict[str, Any]:
        """Get current client usage statistics."""
        return {
            "total_clients": len(self._client_usage),
            "clients": {
                client_id: {
                    "requests_this_hour": data.get("requests_this_hour", 0),
                    "cost_this_hour": data.get("cost_this_hour", 0.0),
                    "last_request": data.get("last_request", 0),
                }
                for client_id, data in self._client_usage.items()
            },
        }

    async def get_usage_summary(self) -> str:
        """Get a brief usage summary for logging/display."""
        usage_stats = await self.usage_tracker.get_current_usage()
        return usage_stats.get_inline_summary()
