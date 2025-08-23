"""
Unified configuration system for MCP Server OpenAI.

Single source of truth for all configuration with environment variable support,
validation, and type safety.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from .error_handler import ConfigurationError
from .logging import get_logger

logger = get_logger("config")


@dataclass
class ServerConfig:
    """Server configuration settings."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "INFO"
    access_log: bool = True


@dataclass
class APIKeysConfig:
    """API keys configuration."""

    openai_api_key: str
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    presenton_api_key: str | None = None
    unsplash_access_key: str | None = None
    pixabay_api_key: str | None = None
    brave_search_api_key: str | None = None
    stable_diffusion_api_key: str | None = None


@dataclass
class FeatureFlags:
    """Feature flags configuration."""

    enable_monitoring: bool = True
    enable_caching: bool = False
    enable_research: bool = True
    enable_image_generation: bool = True
    enable_icon_generation: bool = True
    enable_document_generation: bool = True
    enable_ppt_generation: bool = True
    debug_mode: bool = False


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    validate_api_keys: bool = True
    require_https: bool = False  # Set to True in production
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""

    health_check_timeout: float = 30.0
    metrics_enabled: bool = True
    log_requests: bool = True
    error_tracking: bool = True
    performance_monitoring: bool = True


@dataclass
class CacheConfig:
    """Caching configuration."""

    enabled: bool = False
    redis_url: str | None = None
    default_ttl: int = 3600  # 1 hour
    max_memory: str = "100mb"


@dataclass
class UnifiedConfig:
    """Unified configuration for the entire application."""

    server: ServerConfig = field(default_factory=ServerConfig)
    api_keys: APIKeysConfig = field(default_factory=lambda: APIKeysConfig(openai_api_key=""))
    features: FeatureFlags = field(default_factory=FeatureFlags)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Paths
    data_dir: Path = field(default_factory=lambda: Path("data"))
    output_dir: Path = field(default_factory=lambda: Path("output"))
    logs_dir: Path = field(default_factory=lambda: Path("logs"))
    config_dir: Path = field(default_factory=lambda: Path("config"))

    @classmethod
    def from_env(cls) -> "UnifiedConfig":
        """Load configuration from environment variables."""

        logger.info("Loading configuration from environment variables")

        # Server configuration
        server = ServerConfig(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            workers=int(os.getenv("WORKERS", "1")),
            reload=os.getenv("RELOAD", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            access_log=os.getenv("ACCESS_LOG", "true").lower() == "true",
        )

        # API keys configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ConfigurationError("OPENAI_API_KEY is required but not set", config_key="OPENAI_API_KEY")

        api_keys = APIKeysConfig(
            openai_api_key=openai_key,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            presenton_api_key=os.getenv("PRESENTON_API_KEY"),
            unsplash_access_key=os.getenv("UNSPLASH_ACCESS_KEY"),
            pixabay_api_key=os.getenv("PIXABAY_API_KEY"),
            brave_search_api_key=os.getenv("BRAVE_SEARCH_API_KEY"),
            stable_diffusion_api_key=os.getenv("STABLE_DIFFUSION_API_KEY"),
        )

        # Feature flags
        features = FeatureFlags(
            enable_monitoring=os.getenv("ENABLE_MONITORING", "true").lower() == "true",
            enable_caching=os.getenv("ENABLE_CACHING", "false").lower() == "true",
            enable_research=os.getenv("ENABLE_RESEARCH", "true").lower() == "true",
            enable_image_generation=os.getenv("ENABLE_IMAGE_GENERATION", "true").lower() == "true",
            enable_icon_generation=os.getenv("ENABLE_ICON_GENERATION", "true").lower() == "true",
            enable_document_generation=os.getenv("ENABLE_DOCUMENT_GENERATION", "true").lower() == "true",
            enable_ppt_generation=os.getenv("ENABLE_PPT_GENERATION", "true").lower() == "true",
            debug_mode=os.getenv("DEBUG", "false").lower() == "true",
        )

        # Security configuration
        cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        security = SecurityConfig(
            validate_api_keys=os.getenv("VALIDATE_API_KEYS", "true").lower() == "true",
            require_https=os.getenv("REQUIRE_HTTPS", "false").lower() == "true",
            cors_origins=cors_origins,
            max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(10 * 1024 * 1024))),
            rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "60")),
        )

        # Monitoring configuration
        monitoring = MonitoringConfig(
            health_check_timeout=float(os.getenv("HEALTH_CHECK_TIMEOUT", "30.0")),
            metrics_enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
            log_requests=os.getenv("LOG_REQUESTS", "true").lower() == "true",
            error_tracking=os.getenv("ERROR_TRACKING", "true").lower() == "true",
            performance_monitoring=os.getenv("PERFORMANCE_MONITORING", "true").lower() == "true",
        )

        # Cache configuration
        cache = CacheConfig(
            enabled=os.getenv("CACHE_ENABLED", "false").lower() == "true",
            redis_url=os.getenv("REDIS_URL"),
            default_ttl=int(os.getenv("CACHE_TTL", "3600")),
            max_memory=os.getenv("CACHE_MAX_MEMORY", "100mb"),
        )

        # Paths
        data_dir = Path(os.getenv("DATA_DIR", "data"))
        output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
        logs_dir = Path(os.getenv("LOGS_DIR", "logs"))
        config_dir = Path(os.getenv("CONFIG_DIR", "config"))

        config = cls(
            server=server,
            api_keys=api_keys,
            features=features,
            security=security,
            monitoring=monitoring,
            cache=cache,
            data_dir=data_dir,
            output_dir=output_dir,
            logs_dir=logs_dir,
            config_dir=config_dir,
        )

        # Validate configuration
        config.validate()

        logger.info(
            "Configuration loaded successfully",
            features_enabled=sum(
                [
                    features.enable_monitoring,
                    features.enable_caching,
                    features.enable_research,
                    features.enable_image_generation,
                    features.enable_icon_generation,
                    features.enable_document_generation,
                    features.enable_ppt_generation,
                ]
            ),
        )

        return config

    def validate(self) -> None:
        """Validate configuration settings."""

        # Validate server configuration
        if not (1 <= self.server.port <= 65535):
            raise ConfigurationError(f"Invalid port number: {self.server.port}")

        if self.server.workers < 1:
            raise ConfigurationError(f"Workers must be >= 1, got: {self.server.workers}")

        # Validate API keys
        if not self.api_keys.openai_api_key:
            raise ConfigurationError("OpenAI API key is required")

        if len(self.api_keys.openai_api_key) < 10:
            raise ConfigurationError("OpenAI API key appears to be invalid (too short)")

        # Validate paths and create directories
        for path_name, path in [
            ("data_dir", self.data_dir),
            ("output_dir", self.output_dir),
            ("logs_dir", self.logs_dir),
        ]:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ConfigurationError(f"Cannot create {path_name} directory: {e}") from e

        # Validate cache configuration
        if self.cache.enabled and not self.cache.redis_url:
            logger.warning("Cache enabled but no Redis URL provided, using in-memory cache")

        logger.info("Configuration validation completed successfully")

    def get_api_key(self, service: str) -> str | None:
        """Get API key for a specific service."""
        key_mapping = {
            "openai": self.api_keys.openai_api_key,
            "anthropic": self.api_keys.anthropic_api_key,
            "google": self.api_keys.google_api_key,
            "presenton": self.api_keys.presenton_api_key,
            "unsplash": self.api_keys.unsplash_access_key,
            "pixabay": self.api_keys.pixabay_api_key,
            "brave": self.api_keys.brave_search_api_key,
            "stable_diffusion": self.api_keys.stable_diffusion_api_key,
        }
        return key_mapping.get(service.lower())

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        feature_mapping = {
            "monitoring": self.features.enable_monitoring,
            "caching": self.features.enable_caching,
            "research": self.features.enable_research,
            "image_generation": self.features.enable_image_generation,
            "icon_generation": self.features.enable_icon_generation,
            "document_generation": self.features.enable_document_generation,
            "ppt_generation": self.features.enable_ppt_generation,
            "debug": self.features.debug_mode,
        }
        return feature_mapping.get(feature.lower(), False)


# Global configuration instance
_global_config: UnifiedConfig | None = None


def get_config() -> UnifiedConfig:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = UnifiedConfig.from_env()
    return _global_config


def reload_config() -> UnifiedConfig:
    """Reload configuration from environment."""
    global _global_config
    _global_config = UnifiedConfig.from_env()
    return _global_config
