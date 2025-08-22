"""
Health check and monitoring endpoints for MCP Server OpenAI.

Provides comprehensive health checks for GCP Cloud Run deployment
with proper readiness, liveness, and startup probes.
"""

import asyncio
import logging
import os
import time
from datetime import UTC, datetime
from typing import Any

import httpx
import psutil

from .security import SecureConfig

logger = logging.getLogger(__name__)


class HealthChecker:
    """Comprehensive health checking for the MCP server."""

    def __init__(self):
        self.start_time = datetime.now(UTC)
        self.last_health_check = None
        self.failed_checks = {}
        self.dependency_cache = {}
        self.cache_ttl = 30  # Cache health results for 30 seconds

    async def startup_check(self) -> dict[str, Any]:
        """
        Comprehensive startup health check.
        Used by Cloud Run startup probe.
        """
        checks = {
            "timestamp": datetime.now(UTC).isoformat(),
            "startup_time": (datetime.now(UTC) - self.start_time).total_seconds(),
            "status": "healthy",
            "checks": {},
        }

        try:
            # Configuration validation
            checks["checks"]["config"] = await self._check_configuration()

            # Database connectivity
            checks["checks"]["database"] = await self._check_database()

            # Memory and CPU
            checks["checks"]["resources"] = await self._check_resources()

            # External dependencies (cached)
            checks["checks"]["dependencies"] = await self._check_dependencies()

            # Overall status
            failed_checks = [name for name, check in checks["checks"].items() if check["status"] != "healthy"]

            if failed_checks:
                checks["status"] = "unhealthy"
                checks["failed_checks"] = failed_checks

            self.last_health_check = datetime.now(UTC)

        except Exception as e:
            logger.exception("Startup check failed")
            checks["status"] = "unhealthy"
            checks["error"] = str(e)

        return checks

    async def liveness_check(self) -> dict[str, Any]:
        """
        Liveness probe - determines if container should be restarted.
        Should be lightweight and fast.
        """
        checks = {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "healthy",
            "uptime": (datetime.now(UTC) - self.start_time).total_seconds(),
        }

        try:
            # Basic resource check
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 95:  # Critical memory usage
                checks["status"] = "unhealthy"
                checks["reason"] = f"Critical memory usage: {memory_percent}%"

            # Check if main event loop is responsive
            loop_start = time.time()
            await asyncio.sleep(0.001)  # Tiny sleep to test event loop
            loop_time = time.time() - loop_start

            if loop_time > 1.0:  # Event loop blocked for >1 second
                checks["status"] = "unhealthy"
                checks["reason"] = f"Event loop blocked: {loop_time:.2f}s"

            checks["loop_latency"] = loop_time
            checks["memory_percent"] = memory_percent

        except Exception as e:
            logger.exception("Liveness check failed")
            checks["status"] = "unhealthy"
            checks["error"] = str(e)

        return checks

    async def readiness_check(self) -> dict[str, Any]:
        """
        Readiness probe - determines if container can accept traffic.
        More comprehensive than liveness check.
        """
        checks = {"timestamp": datetime.now(UTC).isoformat(), "status": "healthy", "checks": {}}

        try:
            # Configuration check
            checks["checks"]["config"] = await self._check_configuration()

            # Database connectivity (if configured)
            checks["checks"]["database"] = await self._check_database()

            # Resource availability
            checks["checks"]["resources"] = await self._check_resources()

            # API key validation (cached)
            checks["checks"]["api_keys"] = await self._check_api_keys()

            # Overall readiness
            failed_checks = [name for name, check in checks["checks"].items() if check["status"] != "healthy"]

            if failed_checks:
                checks["status"] = "not_ready"
                checks["failed_checks"] = failed_checks

        except Exception as e:
            logger.exception("Readiness check failed")
            checks["status"] = "not_ready"
            checks["error"] = str(e)

        return checks

    async def detailed_status(self) -> dict[str, Any]:
        """
        Detailed status information for monitoring and debugging.
        """
        status = {
            "timestamp": datetime.now(UTC).isoformat(),
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.now(UTC) - self.start_time).total_seconds(),
            "version": "0.2.0",
            "environment": SecureConfig.get_secret("ENVIRONMENT", "unknown"),
            "status": "healthy",
            "checks": {},
            "metrics": {},
        }

        try:
            # All health checks
            status["checks"]["config"] = await self._check_configuration()
            status["checks"]["database"] = await self._check_database()
            status["checks"]["resources"] = await self._check_resources()
            status["checks"]["dependencies"] = await self._check_dependencies()
            status["checks"]["api_keys"] = await self._check_api_keys()

            # System metrics
            status["metrics"] = self._get_system_metrics()

            # Overall status
            failed_checks = [name for name, check in status["checks"].items() if check["status"] != "healthy"]

            if failed_checks:
                status["status"] = "degraded"
                status["failed_checks"] = failed_checks

        except Exception as e:
            logger.exception("Detailed status check failed")
            status["status"] = "unhealthy"
            status["error"] = str(e)

        return status

    async def _check_configuration(self) -> dict[str, Any]:
        """Check configuration validity."""
        try:
            is_valid, missing = SecureConfig.validate_required_secrets()

            return {
                "status": "healthy" if is_valid else "unhealthy",
                "valid": is_valid,
                "missing_secrets": missing,
                "check_time": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "check_time": datetime.now(UTC).isoformat()}

    async def _check_database(self) -> dict[str, Any]:
        """Check database connectivity."""
        try:
            # This is a placeholder - implement actual database check
            # based on your database setup
            db_url = SecureConfig.get_database_url()

            if not db_url or "sqlite" in db_url:
                # SQLite - just check file exists/writable
                return {"status": "healthy", "type": "sqlite", "check_time": datetime.now(UTC).isoformat()}

            # For PostgreSQL/MySQL - implement actual connection test
            return {"status": "healthy", "type": "postgresql", "check_time": datetime.now(UTC).isoformat()}

        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "check_time": datetime.now(UTC).isoformat()}

    async def _check_resources(self) -> dict[str, Any]:
        """Check system resource availability."""
        try:
            # Memory check
            memory = psutil.virtual_memory()
            memory_healthy = memory.percent < 90

            # CPU check
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_healthy = cpu_percent < 90

            # Disk check
            disk = psutil.disk_usage("/")
            disk_healthy = disk.percent < 90

            overall_healthy = memory_healthy and cpu_healthy and disk_healthy

            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "memory": {
                    "percent": memory.percent,
                    "available_mb": memory.available // (1024 * 1024),
                    "healthy": memory_healthy,
                },
                "cpu": {"percent": cpu_percent, "healthy": cpu_healthy},
                "disk": {
                    "percent": disk.percent,
                    "free_gb": disk.free // (1024 * 1024 * 1024),
                    "healthy": disk_healthy,
                },
                "check_time": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "check_time": datetime.now(UTC).isoformat()}

    async def _check_dependencies(self) -> dict[str, Any]:
        """Check external dependencies with caching."""
        cache_key = "dependencies"
        now = datetime.now(UTC)

        # Check cache first
        if cache_key in self.dependency_cache:
            cached_result, cached_time = self.dependency_cache[cache_key]
            if (now - cached_time).total_seconds() < self.cache_ttl:
                return cached_result

        try:
            dependencies = {}

            # Check OpenAI API
            openai_key = SecureConfig.get_secret("OPENAI_API_KEY")
            if openai_key and openai_key != "COMPROMISED_KEY_REPLACED":
                dependencies["openai"] = await self._test_openai_connection(openai_key)

            # Check Anthropic API
            anthropic_key = SecureConfig.get_secret("ANTHROPIC_API_KEY")
            if anthropic_key and anthropic_key != "COMPROMISED_KEY_REPLACED":
                dependencies["anthropic"] = await self._test_anthropic_connection(anthropic_key)

            # Overall dependency health
            failed_deps = [name for name, dep in dependencies.items() if dep["status"] != "healthy"]

            result = {
                "status": "healthy" if not failed_deps else "degraded",
                "dependencies": dependencies,
                "failed_dependencies": failed_deps,
                "check_time": now.isoformat(),
            }

            # Cache the result
            self.dependency_cache[cache_key] = (result, now)

            return result

        except Exception as e:
            result = {"status": "unhealthy", "error": str(e), "check_time": now.isoformat()}
            return result

    async def _check_api_keys(self) -> dict[str, Any]:
        """Check API key configuration."""
        try:
            api_keys = {}

            # Check each API key
            keys_to_check = [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GOOGLE_API_KEY",
                "UNSPLASH_ACCESS_KEY",
                "PIXABAY_API_KEY",
            ]

            for key_name in keys_to_check:
                key_value = SecureConfig.get_secret(key_name)
                api_keys[key_name] = {
                    "configured": bool(key_value),
                    "valid": bool(key_value) and key_value not in SecureConfig.INVALID_VALUES,
                    "length": len(key_value) if key_value else 0,
                }

            # Count valid keys
            valid_keys = sum(1 for key_info in api_keys.values() if key_info["valid"])
            total_keys = len([key for key in api_keys.values() if key["configured"]])

            return {
                "status": "healthy" if valid_keys > 0 else "unhealthy",
                "valid_keys": valid_keys,
                "total_configured": total_keys,
                "keys": api_keys,
                "check_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "check_time": datetime.now(UTC).isoformat()}

    async def _test_openai_connection(self, api_key: str) -> dict[str, Any]:
        """Test OpenAI API connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {api_key}"}
                )
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def _test_anthropic_connection(self, api_key: str) -> dict[str, Any]:
        """Test Anthropic API connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                )
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _get_system_metrics(self) -> dict[str, Any]:
        """Get current system metrics."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "memory": {
                    "total_mb": memory.total // (1024 * 1024),
                    "available_mb": memory.available // (1024 * 1024),
                    "used_percent": memory.percent,
                },
                "cpu": {"percent": psutil.cpu_percent(interval=0.1), "count": psutil.cpu_count()},
                "disk": {
                    "total_gb": disk.total // (1024 * 1024 * 1024),
                    "free_gb": disk.free // (1024 * 1024 * 1024),
                    "used_percent": disk.percent,
                },
                "process": {"pid": os.getpid(), "threads": psutil.Process().num_threads()},
            }
        except Exception as e:
            logger.exception("Failed to get system metrics")
            return {"error": str(e)}


# Global health checker instance
health_checker = HealthChecker()
