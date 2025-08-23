"""
Security module for MCP Server OpenAI.

Provides secure configuration management, API key validation,
and security utilities for production deployment.
"""

import logging
import os
from datetime import datetime
from typing import Any

from .core.config import get_config
from .core.logging import get_logger

# Initialize core systems
config = get_config()
logger = get_logger("security")


class SecureConfig:
    """Secure configuration management for production deployment."""

    # Known compromised or placeholder values that should never be used
    INVALID_VALUES = {
        "COMPROMISED_KEY_REPLACED",
        "your_api_key_here",
        "your_openai_api_key_here",
        "your_anthropic_api_key_here",
        "your_google_api_key_here",
        "your_unsplash_access_key_here",
        "your_pixabay_api_key_here",
        "",
        "null",
        "None",
    }

    @staticmethod
    def get_secret(key: str, default: str | None = None, required: bool = False) -> str | None:
        """
        Get secret value with proper error handling and validation.

        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether this secret is required for operation

        Returns:
            Secret value or None if not found and not required

        Raises:
            ValueError: If secret is required but missing or invalid
        """
        value = os.getenv(key, default)

        if not value:
            if required:
                logger.error(f"Required secret {key} not found")
                raise ValueError(f"Required API key {key} is missing")
            logger.warning(f"Optional secret {key} not configured")
            return None

        # Check for placeholder/compromised values
        if value in SecureConfig.INVALID_VALUES:
            if required:
                logger.error(f"Secret {key} contains invalid/compromised value")
                raise ValueError(f"Invalid API key for {key} - appears to be placeholder or compromised")
            logger.warning(f"Secret {key} contains placeholder value")
            return None

        # Basic format validation for API keys
        if key.endswith("_API_KEY") and len(value) < 10:
            if required:
                logger.error(f"Secret {key} appears to be too short for a valid API key")
                raise ValueError(f"API key {key} appears to be invalid (too short)")
            logger.warning(f"Secret {key} appears to be invalid")
            return None

        return value

    @staticmethod
    def validate_required_secrets() -> tuple[bool, list[str]]:
        """
        Validate that all required secrets are properly configured.

        Returns:
            Tuple of (is_valid, list_of_missing_secrets)
        """
        required_keys = [
            "OPENAI_API_KEY",
        ]

        optional_keys = [
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "UNSPLASH_ACCESS_KEY",
            "PIXABAY_API_KEY",
        ]

        missing_required = []
        missing_optional = []

        # Check required keys
        for key in required_keys:
            try:
                if not SecureConfig.get_secret(key, required=True):
                    missing_required.append(key)
            except ValueError:
                missing_required.append(key)

        # Check optional keys (warn but don't fail)
        for key in optional_keys:
            if not SecureConfig.get_secret(key, required=False):
                missing_optional.append(key)

        if missing_optional:
            logger.info(f"Optional API keys not configured: {missing_optional}")

        if missing_required:
            logger.error(f"Missing required secrets: {missing_required}")
            return False, missing_required

        logger.info("All required secrets are properly configured")
        return True, []

    @staticmethod
    def get_database_url() -> str | None:
        """Get database URL with preference for production configurations."""
        # Check for Cloud SQL first (production)
        cloud_sql = SecureConfig.get_secret("CLOUD_SQL_CONNECTION_NAME")
        if cloud_sql:
            return f"postgresql+asyncpg://postgres@/{cloud_sql}?unix_sock=/cloudsql/{cloud_sql}/.s.PGSQL.5432"

        # Check for regular PostgreSQL URL
        postgres_url = SecureConfig.get_secret("POSTGRES_URL")
        if postgres_url:
            return postgres_url

        # Fallback to SQLite for development
        sqlite_path = SecureConfig.get_secret("SQLITE_PATH", "data/database.db")
        return f"sqlite+aiosqlite:///{sqlite_path}"


class SecurityLogger:
    """Security event logging utility."""

    def __init__(self) -> None:
        self.security_logger = logging.getLogger("security")

    def log_security_event(self, event_type: str, details: dict[str, Any], level: str = "warning") -> None:
        """
        Log security-related events.

        Args:
            event_type: Type of security event
            details: Event details dictionary
            level: Log level (info, warning, error, critical)
        """
        log_data = {"event_type": event_type, "timestamp": datetime.utcnow().isoformat(), "details": details}

        log_method = getattr(self.security_logger, level.lower(), self.security_logger.warning)
        log_method(f"Security event: {event_type}", extra=log_data)

    def log_auth_failure(self, client_ip: str, endpoint: str, reason: str) -> None:
        """Log authentication failure."""
        self.log_security_event(
            "auth_failure", {"client_ip": client_ip, "endpoint": endpoint, "reason": reason}, "warning"
        )

    def log_rate_limit_exceeded(self, client_ip: str, endpoint: str, limit: int) -> None:
        """Log rate limit exceeded event."""
        self.log_security_event(
            "rate_limit_exceeded", {"client_ip": client_ip, "endpoint": endpoint, "limit": limit}, "warning"
        )

    def log_suspicious_activity(self, client_ip: str, details: dict[str, Any]) -> None:
        """Log suspicious activity."""
        self.log_security_event("suspicious_activity", {"client_ip": client_ip, **details}, "error")


# Global security logger instance
security_logger = SecurityLogger()


def validate_configuration() -> None:
    """
    Validate configuration on startup.

    Raises:
        RuntimeError: If required configuration is missing or invalid
    """
    is_valid, missing_secrets = SecureConfig.validate_required_secrets()

    if not is_valid:
        error_msg = f"Required API keys are not properly configured: {missing_secrets}"
        security_logger.log_security_event("configuration_error", {"missing_secrets": missing_secrets}, "critical")
        raise RuntimeError(error_msg)

    logger.info("Configuration validation completed successfully")


def get_cors_origins() -> list[str]:
    """Get allowed CORS origins from environment."""
    origins_str = SecureConfig.get_secret("ALLOWED_ORIGINS", "http://localhost:3000")
    if origins_str:
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    return ["http://localhost:3000"]


def is_development() -> bool:
    """Check if running in development mode."""
    environment = SecureConfig.get_secret("ENVIRONMENT", "development")
    return (environment or "development").lower() in ("development", "dev", "local")


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled."""
    debug = SecureConfig.get_secret("DEBUG", "false")
    return (debug or "false").lower() in ("true", "1", "yes", "on")


def get_log_level() -> str:
    """Get logging level from environment."""
    level = SecureConfig.get_secret("LOG_LEVEL", "INFO")
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    level_str = (level or "INFO").upper()
    return level_str if level_str in valid_levels else "INFO"
