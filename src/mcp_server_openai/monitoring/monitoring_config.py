"""
Configuration management for enhanced Claude usage monitoring.

Provides configuration classes and utilities for setting up
monitoring, cost limits, token tracking, and alerting thresholds.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class AlertConfig:
    """Configuration for usage alerts and warnings."""

    enabled: bool = True
    warning_threshold: float = 0.8  # 80% of limit
    critical_threshold: float = 0.95  # 95% of limit
    email_alerts: bool = False
    webhook_url: str | None = None
    slack_webhook: str | None = None


@dataclass
class CostLimitsConfig:
    """Configuration for cost and token limits."""

    hourly_max: float = 10.0
    daily_max: float = 100.0
    monthly_max: float = 1000.0
    per_request_max: float = 1.0
    client_hourly_max: float = 1.0  # Per client limit
    tokens_per_hour_max: int = 100000  # Token rate limit
    cache_efficiency_min: float = 0.1  # Minimum cache efficiency warning


@dataclass
class CcusageConfig:
    """Configuration for ccusage integration."""

    enabled: bool = True
    fallback_to_claude_monitor: bool = True
    prefer_bunx: bool = True  # Prefer bunx over npx
    timeout_seconds: float = 10.0
    statusline_format: str = "compact"  # compact, detailed, custom


@dataclass
class MonitoringConfig:
    """Main monitoring configuration with enhanced features."""

    enabled: bool = True
    claude_monitor_enabled: bool = True
    ccusage: CcusageConfig = field(default_factory=CcusageConfig)
    refresh_interval: float = 30.0  # seconds
    cache_duration: float = 10.0  # seconds
    cost_limits: CostLimitsConfig = field(default_factory=CostLimitsConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    rate_limiting_enabled: bool = True
    mock_data_enabled: bool = False  # Use mock data for testing
    log_level: str = "INFO"
    inline_display_enabled: bool = True  # Enable inline cost display

    @classmethod
    def from_env(cls) -> MonitoringConfig:
        """Create config from environment variables."""
        return cls(
            enabled=_get_bool_env("MCP_MONITORING_ENABLED", True),
            claude_monitor_enabled=_get_bool_env("MCP_CLAUDE_MONITOR_ENABLED", True),
            ccusage=CcusageConfig(
                enabled=_get_bool_env("MCP_CCUSAGE_ENABLED", True),
                fallback_to_claude_monitor=_get_bool_env("MCP_CCUSAGE_FALLBACK", True),
                prefer_bunx=_get_bool_env("MCP_CCUSAGE_PREFER_BUNX", True),
                timeout_seconds=_get_float_env("MCP_CCUSAGE_TIMEOUT", 10.0),
                statusline_format=os.getenv("MCP_CCUSAGE_FORMAT", "compact"),
            ),
            refresh_interval=_get_float_env("MCP_MONITORING_REFRESH_INTERVAL", 30.0),
            cache_duration=_get_float_env("MCP_MONITORING_CACHE_DURATION", 10.0),
            cost_limits=CostLimitsConfig(
                hourly_max=_get_float_env("MCP_COST_HOURLY_MAX", 10.0),
                daily_max=_get_float_env("MCP_COST_DAILY_MAX", 100.0),
                monthly_max=_get_float_env("MCP_COST_MONTHLY_MAX", 1000.0),
                per_request_max=_get_float_env("MCP_COST_PER_REQUEST_MAX", 1.0),
                client_hourly_max=_get_float_env("MCP_COST_CLIENT_HOURLY_MAX", 1.0),
                tokens_per_hour_max=_get_int_env("MCP_TOKENS_PER_HOUR_MAX", 100000),
                cache_efficiency_min=_get_float_env("MCP_CACHE_EFFICIENCY_MIN", 0.1),
            ),
            alerts=AlertConfig(
                enabled=_get_bool_env("MCP_ALERTS_ENABLED", True),
                warning_threshold=_get_float_env("MCP_ALERT_WARNING_THRESHOLD", 0.8),
                critical_threshold=_get_float_env("MCP_ALERT_CRITICAL_THRESHOLD", 0.95),
                email_alerts=_get_bool_env("MCP_EMAIL_ALERTS_ENABLED", False),
                webhook_url=os.getenv("MCP_ALERT_WEBHOOK_URL"),
                slack_webhook=os.getenv("MCP_SLACK_WEBHOOK_URL"),
            ),
            rate_limiting_enabled=_get_bool_env("MCP_RATE_LIMITING_ENABLED", True),
            mock_data_enabled=_get_bool_env("MCP_MOCK_DATA_ENABLED", False),
            log_level=os.getenv("MCP_MONITORING_LOG_LEVEL", "INFO"),
            inline_display_enabled=_get_bool_env("MCP_INLINE_DISPLAY_ENABLED", True),
        )

    @classmethod
    def from_yaml(cls, yaml_path: str) -> MonitoringConfig:
        """Create config from YAML file."""
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            monitoring_data = data.get("monitoring", {})

            # Parse ccusage config
            ccusage_data = monitoring_data.get("ccusage", {})
            ccusage = CcusageConfig(
                enabled=ccusage_data.get("enabled", True),
                fallback_to_claude_monitor=ccusage_data.get("fallback_to_claude_monitor", True),
                prefer_bunx=ccusage_data.get("prefer_bunx", True),
                timeout_seconds=ccusage_data.get("timeout_seconds", 10.0),
                statusline_format=ccusage_data.get("statusline_format", "compact"),
            )

            # Parse cost limits
            cost_limits_data = monitoring_data.get("cost_limits", {})
            cost_limits = CostLimitsConfig(
                hourly_max=cost_limits_data.get("hourly_max", 10.0),
                daily_max=cost_limits_data.get("daily_max", 100.0),
                monthly_max=cost_limits_data.get("monthly_max", 1000.0),
                per_request_max=cost_limits_data.get("per_request_max", 1.0),
                client_hourly_max=cost_limits_data.get("client_hourly_max", 1.0),
                tokens_per_hour_max=cost_limits_data.get("tokens_per_hour_max", 100000),
                cache_efficiency_min=cost_limits_data.get("cache_efficiency_min", 0.1),
            )

            # Parse alerts
            alerts_data = monitoring_data.get("alerts", {})
            alerts = AlertConfig(
                enabled=alerts_data.get("enabled", True),
                warning_threshold=alerts_data.get("warning_threshold", 0.8),
                critical_threshold=alerts_data.get("critical_threshold", 0.95),
                email_alerts=alerts_data.get("email_alerts", False),
                webhook_url=alerts_data.get("webhook_url"),
                slack_webhook=alerts_data.get("slack_webhook"),
            )

            return cls(
                enabled=monitoring_data.get("enabled", True),
                claude_monitor_enabled=monitoring_data.get("claude_monitor_enabled", True),
                ccusage=ccusage,
                refresh_interval=monitoring_data.get("refresh_interval", 30.0),
                cache_duration=monitoring_data.get("cache_duration", 10.0),
                cost_limits=cost_limits,
                alerts=alerts,
                rate_limiting_enabled=monitoring_data.get("rate_limiting_enabled", True),
                mock_data_enabled=monitoring_data.get("mock_data_enabled", False),
                log_level=monitoring_data.get("log_level", "INFO"),
                inline_display_enabled=monitoring_data.get("inline_display_enabled", True),
            )

        except Exception:
            # Fall back to default config if YAML parsing fails
            return cls()

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "enabled": self.enabled,
            "claude_monitor_enabled": self.claude_monitor_enabled,
            "ccusage": {
                "enabled": self.ccusage.enabled,
                "fallback_to_claude_monitor": self.ccusage.fallback_to_claude_monitor,
                "prefer_bunx": self.ccusage.prefer_bunx,
                "timeout_seconds": self.ccusage.timeout_seconds,
                "statusline_format": self.ccusage.statusline_format,
            },
            "refresh_interval": self.refresh_interval,
            "cache_duration": self.cache_duration,
            "cost_limits": {
                "hourly_max": self.cost_limits.hourly_max,
                "daily_max": self.cost_limits.daily_max,
                "monthly_max": self.cost_limits.monthly_max,
                "per_request_max": self.cost_limits.per_request_max,
                "client_hourly_max": self.cost_limits.client_hourly_max,
                "tokens_per_hour_max": self.cost_limits.tokens_per_hour_max,
                "cache_efficiency_min": self.cost_limits.cache_efficiency_min,
            },
            "alerts": {
                "enabled": self.alerts.enabled,
                "warning_threshold": self.alerts.warning_threshold,
                "critical_threshold": self.alerts.critical_threshold,
                "email_alerts": self.alerts.email_alerts,
                "webhook_url": self.alerts.webhook_url,
                "slack_webhook": self.alerts.slack_webhook,
            },
            "rate_limiting_enabled": self.rate_limiting_enabled,
            "mock_data_enabled": self.mock_data_enabled,
            "log_level": self.log_level,
            "inline_display_enabled": self.inline_display_enabled,
        }


def get_monitoring_config() -> MonitoringConfig:
    """Get monitoring configuration from environment or file."""
    # Try YAML file first
    yaml_path = os.getenv("MCP_MONITORING_CONFIG_PATH")
    if yaml_path and os.path.exists(yaml_path):
        return MonitoringConfig.from_yaml(yaml_path)

    # Try existing config path
    config_path = os.getenv("MCP_CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        return MonitoringConfig.from_yaml(config_path)

    # Fall back to environment variables
    return MonitoringConfig.from_env()


def _get_bool_env(key: str, default: bool) -> bool:
    """Get boolean environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def _get_float_env(key: str, default: float) -> float:
    """Get float environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def _get_int_env(key: str, default: int) -> int:
    """Get integer environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default
