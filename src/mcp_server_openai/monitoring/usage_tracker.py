"""
Enhanced Claude usage tracking with ccusage integration.

Provides comprehensive token usage tracking, cost analysis, and real-time monitoring
by integrating with ccusage CLI tool for precise Claude Code usage tracking.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ..logging_utils import get_logger

_logger = get_logger("mcp.monitoring.usage")


@dataclass
class TokenUsage:
    """Detailed token usage breakdown."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    total_tokens: int = 0

    @property
    def effective_input_tokens(self) -> int:
        """Input tokens including cache operations."""
        return self.input_tokens + self.cache_creation_tokens

    @property
    def cache_efficiency(self) -> float:
        """Cache hit ratio (0.0 to 1.0)."""
        total_cache = self.cache_creation_tokens + self.cache_read_tokens
        if total_cache == 0:
            return 0.0
        return self.cache_read_tokens / total_cache


@dataclass
class UsageStats:
    """Comprehensive Claude API usage statistics."""

    # Token usage
    tokens: TokenUsage = field(default_factory=TokenUsage)

    # Cost tracking
    cost_usd: float = 0.0
    session_cost: float = 0.0

    # Usage patterns
    requests_count: int = 0
    session_requests: int = 0
    messages_count: int = 0
    session_messages: int = 0
    message_limit: int | None = None  # Daily message limit if known

    # Burn rates
    burn_rate_per_hour: float = 0.0
    burn_rate_per_day: float = 0.0

    # Model information
    model_name: str | None = None

    # Timing
    session_duration_minutes: float = 0.0
    block_time_remaining_minutes: float | None = None
    session_start_time: float | None = None
    five_hour_limit_minutes: float = 300.0  # 5 hours in minutes
    time_until_five_hour_limit: float | None = None  # Minutes remaining

    # Status and warnings
    warnings: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def avg_tokens_per_request(self) -> float:
        """Calculate average tokens per request."""
        return self.tokens.total_tokens / max(self.requests_count, 1)

    @property
    def avg_cost_per_request(self) -> float:
        """Calculate average cost per request."""
        return self.cost_usd / max(self.requests_count, 1)

    @property
    def tokens_per_dollar(self) -> float:
        """Calculate tokens per dollar efficiency."""
        return self.tokens.total_tokens / max(self.cost_usd, 0.001)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tokens": {
                "input_tokens": self.tokens.input_tokens,
                "output_tokens": self.tokens.output_tokens,
                "cache_creation_tokens": self.tokens.cache_creation_tokens,
                "cache_read_tokens": self.tokens.cache_read_tokens,
                "total_tokens": self.tokens.total_tokens,
                "effective_input_tokens": self.tokens.effective_input_tokens,
                "cache_efficiency": round(self.tokens.cache_efficiency, 3),
            },
            "cost_usd": round(self.cost_usd, 4),
            "session_cost": round(self.session_cost, 4),
            "requests_count": self.requests_count,
            "session_requests": self.session_requests,
            "messages_count": self.messages_count,
            "session_messages": self.session_messages,
            "message_limit": self.message_limit,
            "burn_rate_per_hour": round(self.burn_rate_per_hour, 4),
            "burn_rate_per_day": round(self.burn_rate_per_day, 4),
            "model_name": self.model_name,
            "session_duration_minutes": round(self.session_duration_minutes, 1),
            "block_time_remaining_minutes": self.block_time_remaining_minutes,
            "session_start_time": self.session_start_time,
            "five_hour_limit_minutes": self.five_hour_limit_minutes,
            "time_until_five_hour_limit": self.time_until_five_hour_limit,
            "avg_tokens_per_request": round(self.avg_tokens_per_request, 2),
            "avg_cost_per_request": round(self.avg_cost_per_request, 4),
            "tokens_per_dollar": round(self.tokens_per_dollar, 0),
            "warnings": self.warnings,
            "timestamp": self.timestamp,
        }

    def get_inline_summary(self) -> str:
        """Get compact inline summary for display."""
        model_display = self.model_name or "Claude"
        cost_display = f"${self.session_cost:.3f} session / ${self.cost_usd:.2f} today"

        efficiency_parts = []
        if self.burn_rate_per_hour > 0:
            efficiency_parts.append(f"${self.burn_rate_per_hour:.2f}/hr")

        if self.tokens.cache_efficiency > 0:
            efficiency_parts.append(f"{self.tokens.cache_efficiency*100:.0f}% cache")

        if self.block_time_remaining_minutes:
            hours = int(self.block_time_remaining_minutes // 60)
            minutes = int(self.block_time_remaining_minutes % 60)
            efficiency_parts.append(f"{hours}h {minutes}m left")

        efficiency_str = " | ".join(efficiency_parts)

        # Add message count and limits
        message_parts = []
        if self.messages_count > 0:
            if self.message_limit:
                message_parts.append(
                    f"Msgs {self.session_messages}/{self.messages_count} (limit: {self.message_limit})"
                )
            else:
                message_parts.append(f"Msgs {self.session_messages}/{self.messages_count}")

        # Add time remaining for 5-hour limit
        if self.time_until_five_hour_limit is not None:
            hours = int(self.time_until_five_hour_limit // 60)
            minutes = int(self.time_until_five_hour_limit % 60)
            message_parts.append(f"Time {hours}h{minutes}m left")

        # Add block time remaining if different from 5-hour limit
        if (
            self.block_time_remaining_minutes
            and abs(self.block_time_remaining_minutes - (self.time_until_five_hour_limit or 0)) > 5
        ):
            hours = int(self.block_time_remaining_minutes // 60)
            minutes = int(self.block_time_remaining_minutes % 60)
            message_parts.append(f"Block {hours}h{minutes}m")

        message_str = " | ".join(message_parts)

        # Combine all parts
        parts = [f"Claude {model_display}", f"Cost {cost_display}"]
        if efficiency_str:
            parts.append(f"Rate {efficiency_str}")
        if message_str:
            parts.append(message_str)
        parts.append(f"Tokens {self.tokens.total_tokens:,}")

        return " | ".join(parts)


class EnhancedUsageTracker:
    """Enhanced usage tracker with ccusage and claude-monitor integration."""

    def __init__(self, refresh_interval: float = 30.0):
        self.refresh_interval = refresh_interval
        self._last_stats: UsageStats | None = None
        self._last_refresh: float = 0.0
        self._cache_duration = 10.0  # Cache stats for 10 seconds
        self._session_start = time.time()

    async def get_current_usage(self, force_refresh: bool = False) -> UsageStats:
        """Get current usage statistics with caching."""
        now = time.time()

        # Use cached stats if recent enough
        if not force_refresh and self._last_stats and now - self._last_refresh < self._cache_duration:
            return self._last_stats

        # Fetch fresh stats
        stats = await self._get_combined_usage_stats()
        self._last_stats = stats
        self._last_refresh = now

        return stats

    async def track_api_call(
        self, input_tokens: int, output_tokens: int, cost: float, model: str | None = None, message_count: int = 1
    ) -> None:
        """Track a single API call for session statistics."""
        if self._last_stats:
            # Update session stats
            self._last_stats.tokens.input_tokens += input_tokens
            self._last_stats.tokens.output_tokens += output_tokens
            self._last_stats.tokens.total_tokens += input_tokens + output_tokens
            self._last_stats.session_cost += cost
            self._last_stats.session_requests += 1
            self._last_stats.session_messages += message_count
            if model:
                self._last_stats.model_name = model

        _logger.info(
            "API call tracked",
            extra={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "model": model,
                "event_type": "api_usage_tracked",
            },
        )

    async def get_statusline_display(self) -> str:
        """Get compact statusline display suitable for Claude Code status bar."""
        stats = await self.get_current_usage()
        return stats.get_inline_summary()

    async def _get_combined_usage_stats(self) -> UsageStats:
        """Get usage stats from ccusage and claude-monitor tools."""
        # Try ccusage first (more accurate for Claude Code usage)
        ccusage_stats = await self._get_ccusage_stats()
        if ccusage_stats:
            return ccusage_stats

        # Fall back to claude-monitor
        claude_monitor_stats = await self._get_claude_monitor_stats()
        if claude_monitor_stats:
            return claude_monitor_stats

        # Fall back to mock data
        return self._get_mock_usage_stats()

    async def _get_ccusage_stats(self) -> UsageStats | None:
        """Get usage stats from ccusage tool."""
        try:
            # Try different ccusage execution methods
            for cmd_args in [
                ["bunx", "ccusage", "daily", "--json"],
                ["npx", "ccusage@latest", "daily", "--json"],
                ["ccusage", "daily", "--json"],
            ]:
                try:
                    result = await asyncio.create_subprocess_exec(
                        *cmd_args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=10.0)

                    if result.returncode == 0 and stdout:
                        try:
                            data = json.loads(stdout.decode())
                            return self._parse_ccusage_output(data)
                        except json.JSONDecodeError as e:
                            _logger.warning(f"Failed to parse ccusage JSON: {e}")
                            continue

                except FileNotFoundError:
                    continue  # Try next command
                except Exception as e:
                    _logger.debug(f"ccusage command {cmd_args} failed: {e}")
                    continue

            _logger.info("ccusage not available, falling back to claude-monitor")
            return None

        except Exception as e:
            _logger.error(f"Error getting ccusage stats: {e}")
            return None

    async def _get_claude_monitor_stats(self) -> UsageStats | None:
        """Get usage stats from claude-monitor tool."""
        try:
            result = await asyncio.create_subprocess_exec(
                "claude-monitor",
                "--output",
                "json",
                "--no-interactive",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=5.0)

            if result.returncode == 0 and stdout:
                try:
                    data = json.loads(stdout.decode())
                    return self._parse_claude_monitor_output(data)
                except json.JSONDecodeError as e:
                    _logger.warning(f"Failed to parse claude-monitor JSON: {e}")

            return None

        except (TimeoutError, FileNotFoundError, Exception) as e:
            _logger.debug(f"claude-monitor not available: {e}")
            return None

    def _parse_ccusage_output(self, data: dict[str, Any]) -> UsageStats:
        """Parse ccusage output into UsageStats."""
        # ccusage provides detailed token and cost information
        tokens = TokenUsage(
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            cache_creation_tokens=data.get("cache_creation_tokens", 0),
            cache_read_tokens=data.get("cache_read_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )

        session_duration = (time.time() - self._session_start) / 60.0  # minutes

        # Calculate 5-hour limit timing
        five_hour_limit_minutes = 300.0  # 5 hours
        session_start_time = self._session_start
        time_until_five_hour_limit = max(0, five_hour_limit_minutes - session_duration)

        return UsageStats(
            tokens=tokens,
            cost_usd=data.get("total_cost", 0.0),
            session_cost=data.get("session_cost", 0.0),
            requests_count=data.get("total_requests", 0),
            session_requests=data.get("session_requests", 0),
            messages_count=data.get("total_messages", data.get("total_requests", 0)),  # Fallback to requests
            session_messages=data.get("session_messages", data.get("session_requests", 0)),  # Fallback to requests
            message_limit=data.get("message_limit"),
            burn_rate_per_hour=data.get("hourly_burn_rate", 0.0),
            burn_rate_per_day=data.get("daily_burn_rate", 0.0),
            model_name=data.get("model", "Claude"),
            session_duration_minutes=session_duration,
            block_time_remaining_minutes=data.get("block_time_remaining_minutes"),
            session_start_time=session_start_time,
            five_hour_limit_minutes=five_hour_limit_minutes,
            time_until_five_hour_limit=time_until_five_hour_limit,
            warnings=data.get("warnings", []),
        )

    def _parse_claude_monitor_output(self, data: dict[str, Any]) -> UsageStats:
        """Parse claude-monitor output into UsageStats."""
        tokens = TokenUsage(
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )

        session_duration = (time.time() - self._session_start) / 60.0  # minutes

        # Calculate 5-hour limit timing
        five_hour_limit_minutes = 300.0  # 5 hours
        session_start_time = self._session_start
        time_until_five_hour_limit = max(0, five_hour_limit_minutes - session_duration)

        return UsageStats(
            tokens=tokens,
            cost_usd=data.get("total_cost", 0.0),
            requests_count=data.get("total_requests", 0),
            messages_count=data.get("total_messages", data.get("total_requests", 0)),
            session_messages=data.get("session_messages", 0),
            message_limit=data.get("message_limit"),
            burn_rate_per_hour=data.get("hourly_burn_rate", 0.0),
            burn_rate_per_day=data.get("daily_burn_rate", 0.0),
            session_duration_minutes=session_duration,
            session_start_time=session_start_time,
            five_hour_limit_minutes=five_hour_limit_minutes,
            time_until_five_hour_limit=time_until_five_hour_limit,
            warnings=data.get("warnings", []),
        )

    def _get_mock_usage_stats(self) -> UsageStats:
        """Return mock usage stats for development/testing."""
        import random

        # Generate realistic mock data
        base_input_tokens = random.randint(500, 10000)
        base_output_tokens = random.randint(200, 5000)
        cache_creation = random.randint(0, base_input_tokens // 3)
        cache_read = random.randint(0, base_input_tokens // 2)

        tokens = TokenUsage(
            input_tokens=base_input_tokens,
            output_tokens=base_output_tokens,
            cache_creation_tokens=cache_creation,
            cache_read_tokens=cache_read,
            total_tokens=base_input_tokens + base_output_tokens + cache_creation,
        )

        base_cost = tokens.total_tokens * 0.00001  # Rough estimate
        session_duration = (time.time() - self._session_start) / 60.0  # minutes

        # Calculate 5-hour limit timing
        five_hour_limit_minutes = 300.0  # 5 hours
        session_start_time = self._session_start
        time_until_five_hour_limit = max(0, five_hour_limit_minutes - session_duration)

        # Generate mock message counts
        total_messages = random.randint(20, 200)
        session_messages = random.randint(1, min(50, total_messages))
        message_limit = random.choice([None, 200, 500, 1000])  # Some accounts have limits

        return UsageStats(
            tokens=tokens,
            cost_usd=base_cost,
            session_cost=base_cost * random.uniform(0.1, 0.5),
            requests_count=random.randint(10, 100),
            session_requests=random.randint(1, 20),
            messages_count=total_messages,
            session_messages=session_messages,
            message_limit=message_limit,
            burn_rate_per_hour=base_cost * random.uniform(0.5, 2.0),
            burn_rate_per_day=base_cost * random.uniform(12, 30),
            model_name=random.choice(["Claude-3.5-Sonnet", "Claude-3-Opus", "Claude-3-Haiku"]),
            session_duration_minutes=session_duration,
            block_time_remaining_minutes=random.randint(60, 300) if random.random() > 0.5 else None,
            session_start_time=session_start_time,
            five_hour_limit_minutes=five_hour_limit_minutes,
            time_until_five_hour_limit=time_until_five_hour_limit,
            warnings=[] if random.random() > 0.3 else ["Mock warning: High usage detected"],
        )

    async def check_usage_limits(self, hourly_limit: float, daily_limit: float) -> dict[str, Any]:
        """Check if current usage is within specified limits."""
        stats = await self.get_current_usage()

        # Check limits
        within_limits = stats.burn_rate_per_hour <= hourly_limit and stats.burn_rate_per_day <= daily_limit

        warnings = []
        if stats.burn_rate_per_hour > hourly_limit * 0.8:
            warnings.append(f"Approaching hourly limit: ${stats.burn_rate_per_hour:.2f}/${hourly_limit:.2f}")
        if stats.burn_rate_per_day > daily_limit * 0.8:
            warnings.append(f"Approaching daily limit: ${stats.burn_rate_per_day:.2f}/${daily_limit:.2f}")

        return {
            "within_limits": within_limits,
            "warnings": warnings,
            "limits": {
                "hourly_max": hourly_limit,
                "daily_max": daily_limit,
                "current_hourly": stats.burn_rate_per_hour,
                "current_daily": stats.burn_rate_per_day,
            },
        }


# Convenience functions for backward compatibility
async def get_claude_usage_stats() -> UsageStats:
    """Get current Claude usage stats (legacy interface)."""
    tracker = EnhancedUsageTracker()
    return await tracker.get_current_usage()


async def get_inline_usage_display() -> str:
    """Get inline usage display for status bars."""
    tracker = EnhancedUsageTracker()
    return await tracker.get_statusline_display()
