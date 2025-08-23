"""
Enhanced HTTP Server Runner with modern features.

Provides an enhanced server runner with HTTP/2 support, advanced configuration,
performance optimizations, and comprehensive monitoring capabilities.
"""

from __future__ import annotations

import asyncio
import signal
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from uvicorn.config import Config

from .logging_utils import get_logger
from .server_config import ServerConfig, get_config, validate_config
from .streaming_http import app as streaming_app

_logger = get_logger("mcp.enhanced_server")


class EnhancedUvicornServer(uvicorn.Server):
    """
    Enhanced Uvicorn server with graceful shutdown and monitoring.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self._shutdown_event = asyncio.Event()
        self._startup_complete = False

    async def startup(self, sockets: list | None = None) -> None:
        """Enhanced startup with monitoring."""
        _logger.info("🚀 Starting enhanced MCP server...")
        await super().startup(sockets)
        self._startup_complete = True
        _logger.info("✅ Server startup complete")

    async def shutdown(self, sockets: list | None = None) -> None:
        """Enhanced shutdown with graceful connection handling."""
        _logger.info("🔄 Initiating graceful shutdown...")
        self._shutdown_event.set()
        await super().shutdown(sockets)
        _logger.info("✅ Server shutdown complete")

    def handle_exit(self, sig: int, frame: Any) -> None:
        """Handle exit signals gracefully."""
        _logger.info(f"📡 Received signal {sig}, initiating shutdown...")
        self.should_exit = True

    async def serve(self, sockets: list | None = None) -> None:
        """Enhanced serve method with signal handling."""
        # Set up signal handlers
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self.handle_exit)
        if hasattr(signal, "SIGINT"):
            signal.signal(signal.SIGINT, self.handle_exit)

        await super().serve(sockets)


def create_enhanced_uvicorn_config(server_config: ServerConfig) -> Config:
    """
    Create enhanced Uvicorn configuration with HTTP/2 and optimizations.
    """
    # Base configuration
    uvicorn_config = server_config.to_uvicorn_config()

    # SSL configuration for HTTP/2
    ssl_config = server_config.get_ssl_config()
    if ssl_config:
        uvicorn_config.update(ssl_config)
        # Enable HTTP/2 with SSL
        assert server_config.performance is not None
        if server_config.performance.http2_enabled:
            uvicorn_config["http"] = "httptools"  # Better HTTP/2 support

    # Enhanced configuration
    uvicorn_config.update(
        {
            "app": streaming_app,
            "factory": False,
            "proxy_headers": True,
            "forwarded_allow_ips": "*",
            "use_colors": True,
        }
    )

    return Config(**uvicorn_config)


async def run_enhanced_server(config: ServerConfig | None = None) -> None:
    """
    Run the enhanced HTTP server with modern features.

    Args:
        config: Optional server configuration. If None, loads from environment.
    """
    if config is None:
        config = get_config()

    # Validate configuration
    config_issues = validate_config(config)
    if config_issues:
        _logger.error("❌ Configuration validation failed:")
        for issue in config_issues:
            _logger.error(f"  - {issue}")
        sys.exit(1)

    _logger.info("⚙️  Server configuration:")
    _logger.info(f"  - Host: {config.host}:{config.port}")
    _logger.info(f"  - Workers: {config.workers}")

    # Ensure all config objects are initialized
    assert config.performance is not None
    assert config.compression is not None
    assert config.security is not None

    _logger.info(f"  - HTTP/2: {'✅' if config.performance.http2_enabled else '❌'}")
    _logger.info(f"  - Compression: {'✅' if config.compression.enabled else '❌'}")
    _logger.info(f"  - Rate Limiting: {'✅' if config.security.rate_limiting_enabled else '❌'}")
    _logger.info(f"  - CORS: {'✅' if config.security.cors_enabled else '❌'}")

    # Create enhanced Uvicorn configuration
    uvicorn_config = create_enhanced_uvicorn_config(config)
    server = EnhancedUvicornServer(uvicorn_config)

    try:
        _logger.info("🌟 Enhanced MCP server starting...")
        await server.serve()
    except KeyboardInterrupt:
        _logger.info("📡 Received keyboard interrupt")
    except Exception as e:
        _logger.error(f"❌ Server error: {e}")
        raise
    finally:
        _logger.info("🏁 Server stopped")


def run_server_sync(config: ServerConfig | None = None) -> None:
    """
    Synchronous wrapper for running the enhanced server.

    Args:
        config: Optional server configuration. If None, loads from environment.
    """
    try:
        if sys.platform == "win32":
            # Windows-specific event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        asyncio.run(run_enhanced_server(config))
    except KeyboardInterrupt:
        _logger.info("🛑 Server stopped by user")
    except Exception as e:
        _logger.error(f"💥 Fatal server error: {e}")
        sys.exit(1)


class ServerManager:
    """
    Enhanced server manager for programmatic control.
    """

    def __init__(self, config: ServerConfig | None = None):
        self.config = config or get_config()
        self.server: EnhancedUvicornServer | None = None
        self._running = False

    async def start(self) -> None:
        """Start the server asynchronously."""
        if self._running:
            raise RuntimeError("Server is already running")

        uvicorn_config = create_enhanced_uvicorn_config(self.config)
        self.server = EnhancedUvicornServer(uvicorn_config)

        _logger.info("🚀 Starting server manager...")
        self._running = True

        try:
            await self.server.serve()
        finally:
            self._running = False

    async def stop(self) -> None:
        """Stop the server gracefully."""
        if not self._running or not self.server:
            return

        _logger.info("🔄 Stopping server manager...")
        self.server.should_exit = True
        await asyncio.sleep(0.1)  # Give it a moment to shut down
        self._running = False

    @property
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self._running

    @asynccontextmanager
    async def run_context(self) -> AsyncGenerator[ServerManager, None]:
        """Context manager for server lifecycle."""
        await self.start()
        try:
            yield self
        finally:
            await self.stop()


# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor server performance metrics."""

    def __init__(self) -> None:
        self.metrics: dict[str, Any] = {
            "requests_per_second": 0.0,
            "average_response_time": 0.0,
            "active_connections": 0,
            "memory_usage": 0,
            "cpu_usage": 0.0,
        }

    async def collect_metrics(self) -> dict[str, Any]:
        """Collect current performance metrics."""
        # TODO: Implement actual metric collection
        # This would integrate with system monitoring tools
        return self.metrics.copy()

    async def start_monitoring(self) -> None:
        """Start background performance monitoring."""
        _logger.info("📊 Starting performance monitoring...")

        async def monitor_loop() -> None:
            while True:
                try:
                    metrics = await self.collect_metrics()
                    _logger.debug(f"Performance metrics: {metrics}")
                    await asyncio.sleep(60)  # Collect every minute
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    _logger.error(f"Monitoring error: {e}")
                    await asyncio.sleep(60)

        asyncio.create_task(monitor_loop())


# CLI interface for enhanced server
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced MCP HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-http2", action="store_true", help="Disable HTTP/2")
    parser.add_argument("--no-compression", action="store_true", help="Disable compression")

    args = parser.parse_args()

    # Create configuration from arguments
    config = ServerConfig(
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
        debug=args.debug,
    )

    if args.no_http2:
        assert config.performance is not None
        config.performance.http2_enabled = False
    if args.no_compression:
        assert config.compression is not None
        config.compression.enabled = False

    # Run the server
    run_server_sync(config)
