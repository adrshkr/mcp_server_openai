"""
Enhanced HTTP Server Configuration.

Provides configuration management for the modern streamable HTTP server
with support for HTTP/2, compression, security, and performance tuning.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class CompressionConfig:
    """Compression configuration settings."""

    enabled: bool = True
    algorithms: list[str] | None = None
    min_size: int = 1000  # Minimum size in bytes to compress
    gzip_level: int = 6
    brotli_level: int = 4

    def __post_init__(self) -> None:
        if self.algorithms is None:
            self.algorithms = ["gzip", "brotli", "deflate"]


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    cors_enabled: bool = True
    cors_origins: list[str] | None = None
    cors_methods: list[str] | None = None
    cors_headers: list[str] | None = None
    rate_limiting_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: str = "1/minute"
    security_headers_enabled: bool = True
    https_redirect: bool = False

    def __post_init__(self) -> None:
        if self.cors_origins is None:
            self.cors_origins = ["*"]
        if self.cors_methods is None:
            self.cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        if self.cors_headers is None:
            self.cors_headers = ["*"]


@dataclass
class ConnectionConfig:
    """Connection management configuration."""

    max_connections: int = 1000
    keep_alive_timeout: int = 75
    heartbeat_interval: int = 30
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    sse_heartbeat_interval: int = 10
    graceful_shutdown_timeout: int = 30


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""

    http2_enabled: bool = True
    connection_pooling: bool = True
    response_caching: bool = False
    cache_ttl: int = 300
    streaming_chunk_size: int = 8192
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    worker_connections: int = 1000


@dataclass
class LoggingConfig:
    """Logging configuration for the HTTP server."""

    access_log_enabled: bool = True
    access_log_format: str = "combined"
    error_log_enabled: bool = True
    performance_logging: bool = True
    request_id_header: str = "X-Request-ID"
    log_level: str = "INFO"


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration."""

    metrics_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    health_check_endpoint: str = "/health"
    prometheus_format: bool = True
    custom_metrics: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.custom_metrics is None:
            self.custom_metrics = {}


@dataclass
class ServerConfig:
    """Main server configuration combining all settings."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    compression: CompressionConfig | None = None
    security: SecurityConfig | None = None
    connections: ConnectionConfig | None = None
    performance: PerformanceConfig | None = None
    logging: LoggingConfig | None = None
    monitoring: MonitoringConfig | None = None
    debug: bool = False
    reload: bool = False

    def __post_init__(self) -> None:
        if self.compression is None:
            self.compression = CompressionConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.connections is None:
            self.connections = ConnectionConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()

    @classmethod
    def from_env(cls) -> ServerConfig:
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("MCP_HTTP_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_HTTP_PORT", "8000")),
            workers=int(os.getenv("MCP_HTTP_WORKERS", "1")),
            debug=os.getenv("MCP_HTTP_DEBUG", "false").lower() == "true",
            reload=os.getenv("MCP_HTTP_RELOAD", "false").lower() == "true",
            compression=CompressionConfig(
                enabled=os.getenv("MCP_COMPRESSION_ENABLED", "true").lower() == "true",
                min_size=int(os.getenv("MCP_COMPRESSION_MIN_SIZE", "1000")),
                gzip_level=int(os.getenv("MCP_GZIP_LEVEL", "6")),
            ),
            security=SecurityConfig(
                cors_enabled=os.getenv("MCP_CORS_ENABLED", "true").lower() == "true",
                cors_origins=os.getenv("MCP_CORS_ORIGINS", "*").split(","),
                rate_limiting_enabled=os.getenv("MCP_RATE_LIMITING", "true").lower() == "true",
                rate_limit_requests=int(os.getenv("MCP_RATE_LIMIT_REQUESTS", "100")),
            ),
            connections=ConnectionConfig(
                max_connections=int(os.getenv("MCP_MAX_CONNECTIONS", "1000")),
                keep_alive_timeout=int(os.getenv("MCP_KEEP_ALIVE_TIMEOUT", "75")),
                heartbeat_interval=int(os.getenv("MCP_HEARTBEAT_INTERVAL", "30")),
            ),
            performance=PerformanceConfig(
                http2_enabled=os.getenv("MCP_HTTP2_ENABLED", "true").lower() == "true",
                connection_pooling=os.getenv("MCP_CONNECTION_POOLING", "true").lower() == "true",
                max_request_size=int(os.getenv("MCP_MAX_REQUEST_SIZE", str(10 * 1024 * 1024))),
            ),
            logging=LoggingConfig(
                access_log_enabled=os.getenv("MCP_ACCESS_LOG", "true").lower() == "true",
                error_log_enabled=os.getenv("MCP_ERROR_LOG", "true").lower() == "true",
                log_level=os.getenv("MCP_LOG_LEVEL", "INFO").upper(),
            ),
        )

    def to_uvicorn_config(self) -> dict[str, Any]:
        """Convert to uvicorn configuration dictionary."""
        # Ensure all config objects are initialized
        assert self.logging is not None
        assert self.connections is not None

        return {
            "host": self.host,
            "port": self.port,
            "workers": self.workers,
            "reload": self.reload,
            "access_log": self.logging.access_log_enabled,
            "log_level": self.logging.log_level.lower(),
            "loop": "asyncio",
            "http": "h11",  # Use h11 for HTTP/1.1, httptools for HTTP/2
            "interface": "asgi3",
            "lifespan": "on",
            "server_header": False,
            "date_header": True,
            "timeout_keep_alive": self.connections.keep_alive_timeout,
            "timeout_graceful_shutdown": self.connections.graceful_shutdown_timeout,
            "limit_max_requests": None,
            "limit_concurrency": self.connections.max_connections,
        }

    def get_ssl_config(self) -> dict[str, Any] | None:
        """Get SSL configuration if available."""
        ssl_keyfile = os.getenv("MCP_SSL_KEYFILE")
        ssl_certfile = os.getenv("MCP_SSL_CERTFILE")

        if ssl_keyfile and ssl_certfile:
            return {
                "ssl_keyfile": ssl_keyfile,
                "ssl_certfile": ssl_certfile,
                "ssl_version": "TLSv1_2",
                "ssl_cert_reqs": "CERT_NONE",
                "ssl_ca_certs": os.getenv("MCP_SSL_CA_CERTS"),
                "ssl_ciphers": "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS",
            }
        return None


# Default configuration instance
default_config = ServerConfig()


def get_config() -> ServerConfig:
    """Get server configuration from environment or defaults."""
    return ServerConfig.from_env()


def validate_config(config: ServerConfig) -> list[str]:
    """Validate server configuration and return any issues."""
    issues = []

    if config.port < 1 or config.port > 65535:
        issues.append(f"Invalid port number: {config.port}")

    if config.workers < 1:
        issues.append(f"Invalid worker count: {config.workers}")

    # Ensure all config objects are initialized
    assert config.compression is not None
    assert config.connections is not None
    assert config.performance is not None

    if config.compression.gzip_level < 1 or config.compression.gzip_level > 9:
        issues.append(f"Invalid gzip compression level: {config.compression.gzip_level}")

    if config.connections.max_connections < 1:
        issues.append(f"Invalid max connections: {config.connections.max_connections}")

    if config.performance.max_request_size < 1024:
        issues.append(f"Max request size too small: {config.performance.max_request_size}")

    return issues
