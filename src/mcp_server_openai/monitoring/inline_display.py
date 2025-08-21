"""
Inline cost and token usage display utilities.

Provides real-time usage information for status bars, logs, and command-line interfaces.
"""

from __future__ import annotations

import asyncio
import time

from ..logging_utils import get_logger
from .monitoring_config import get_monitoring_config
from .usage_tracker import EnhancedUsageTracker

_logger = get_logger("mcp.monitoring.display")


class InlineDisplayManager:
    """Manages inline cost and token usage displays."""

    def __init__(self):
        self.config = get_monitoring_config()
        self.tracker = EnhancedUsageTracker(refresh_interval=self.config.refresh_interval)
        self._last_display_update = 0.0
        self._cached_display = ""

    async def get_statusline_display(self, force_refresh: bool = False) -> str:
        """Get formatted statusline display for Claude Code status bar."""
        if not self.config.inline_display_enabled:
            return ""

        now = time.time()
        if not force_refresh and self._cached_display and now - self._last_display_update < self.config.cache_duration:
            return self._cached_display

        try:
            display = await self.tracker.get_statusline_display()
            self._cached_display = display
            self._last_display_update = now
            return display
        except Exception as e:
            _logger.error(f"Error generating statusline display: {e}")
            return "🤖 Claude | 💰 Error retrieving usage data"

    async def get_compact_summary(self) -> str:
        """Get compact usage summary for logging."""
        try:
            stats = await self.tracker.get_current_usage()
            return (
                f"Session: ${stats.session_cost:.3f} | "
                f"Today: ${stats.cost_usd:.2f} | "
                f"Tokens: {stats.tokens.total_tokens:,} | "
                f"Rate: ${stats.burn_rate_per_hour:.2f}/hr"
            )
        except Exception as e:
            _logger.error(f"Error generating compact summary: {e}")
            return "Usage data unavailable"

    async def get_detailed_summary(self) -> dict:
        """Get detailed usage information for debugging."""
        try:
            stats = await self.tracker.get_current_usage()
            return {
                "summary": stats.get_inline_summary(),
                "detailed_stats": stats.to_dict(),
                "cache_efficiency": f"{stats.tokens.cache_efficiency * 100:.1f}%",
                "session_duration": f"{stats.session_duration_minutes:.1f} minutes",
                "efficiency_metrics": {
                    "tokens_per_dollar": stats.tokens_per_dollar,
                    "avg_cost_per_request": stats.avg_cost_per_request,
                    "avg_tokens_per_request": stats.avg_tokens_per_request,
                },
            }
        except Exception as e:
            _logger.error(f"Error generating detailed summary: {e}")
            return {"error": str(e)}

    async def log_usage_update(self, level: str = "INFO") -> None:
        """Log current usage to the logger."""
        try:
            summary = await self.get_compact_summary()
            if level.upper() == "DEBUG":
                detailed = await self.get_detailed_summary()
                _logger.debug(f"Usage Update: {summary}", extra=detailed)
            else:
                _logger.info(f"Usage Update: {summary}")
        except Exception as e:
            _logger.error(f"Error logging usage update: {e}")


# Global display manager instance
_display_manager: InlineDisplayManager | None = None


def get_display_manager() -> InlineDisplayManager:
    """Get or create the global display manager instance."""
    global _display_manager
    if _display_manager is None:
        _display_manager = InlineDisplayManager()
    return _display_manager


async def get_statusline() -> str:
    """Convenience function to get statusline display."""
    manager = get_display_manager()
    return await manager.get_statusline_display()


async def get_usage_summary() -> str:
    """Convenience function to get usage summary."""
    manager = get_display_manager()
    return await manager.get_compact_summary()


async def log_current_usage() -> None:
    """Convenience function to log current usage."""
    manager = get_display_manager()
    await manager.log_usage_update()


class UsageMiddleware:
    """Middleware for automatically tracking and displaying usage in web requests."""

    def __init__(self, app, log_interval: float = 300.0):  # Log every 5 minutes
        self.app = app
        self.log_interval = log_interval
        self._last_log = 0.0
        self.display_manager = get_display_manager()

    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation."""
        # Track usage at regular intervals
        now = time.time()
        if now - self._last_log > self.log_interval:
            asyncio.create_task(self._log_usage_async())
            self._last_log = now

        # Continue with the request
        await self.app(scope, receive, send)

    async def _log_usage_async(self):
        """Log usage asynchronously."""
        try:
            await self.display_manager.log_usage_update()
        except Exception as e:
            _logger.error(f"Error in usage middleware: {e}")


def create_status_command() -> str:
    """Create a shell command for status line integration."""
    # This creates a command that can be used in Claude Code status line
    return (
        'python -c "'
        "import asyncio; "
        "from mcp_server_openai.monitoring.inline_display import get_statusline; "
        'print(asyncio.run(get_statusline()))"'
    )


def create_ccusage_fallback_command() -> str:
    """Create a fallback command using ccusage directly."""
    return "bunx ccusage statusline || npx ccusage@latest statusline || echo '🤖 Claude | 💰 Usage data unavailable'"
