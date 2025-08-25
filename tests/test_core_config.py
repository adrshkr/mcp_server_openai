"""
Tests for the unified configuration system.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mcp_server_openai.core.config import (
    APIKeysConfig,
    CacheConfig,
    FeatureFlags,
    MonitoringConfig,
    SecurityConfig,
    ServerConfig,
    UnifiedConfig,
    get_config,
    reload_config,
)
from mcp_server_openai.core.error_handler import ConfigurationError


class TestServerConfig:
    """Test ServerConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ServerConfig()

        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.workers == 1
        assert config.reload is False
        assert config.log_level == "INFO"
        assert config.access_log is True


class TestAPIKeysConfig:
    """Test APIKeysConfig dataclass."""

    def test_required_openai_key(self):
        """Test that OpenAI key is required."""
        config = APIKeysConfig(openai_api_key="test-key")

        assert config.openai_api_key == "test-key"
        assert config.anthropic_api_key is None

    def test_all_keys_provided(self):
        """Test configuration with all API keys."""
        config = APIKeysConfig(
            openai_api_key="openai-key",
            anthropic_api_key="anthropic-key",
            google_api_key="google-key",
            unsplash_access_key="unsplash-key",
        )

        assert config.openai_api_key == "openai-key"
        assert config.anthropic_api_key == "anthropic-key"
        assert config.google_api_key == "google-key"
        assert config.unsplash_access_key == "unsplash-key"


class TestFeatureFlags:
    """Test FeatureFlags dataclass."""

    def test_default_features(self):
        """Test default feature flag values."""
        flags = FeatureFlags()

        assert flags.enable_monitoring is True
        assert flags.enable_caching is False
        assert flags.enable_research is True
        assert flags.debug_mode is False


class TestUnifiedConfig:
    """Test UnifiedConfig class."""

    def test_default_config_creation(self):
        """Test creating config with defaults."""
        config = UnifiedConfig()

        assert isinstance(config.server, ServerConfig)
        assert isinstance(config.features, FeatureFlags)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.monitoring, MonitoringConfig)
        assert isinstance(config.cache, CacheConfig)

    def test_get_api_key(self):
        """Test getting API keys by service name."""
        api_keys = APIKeysConfig(openai_api_key="openai-key", anthropic_api_key="anthropic-key")
        config = UnifiedConfig(api_keys=api_keys)

        assert config.get_api_key("openai") == "openai-key"
        assert config.get_api_key("anthropic") == "anthropic-key"
        assert config.get_api_key("google") is None
        assert config.get_api_key("unknown") is None

    def test_is_feature_enabled(self):
        """Test checking if features are enabled."""
        features = FeatureFlags(enable_monitoring=True, enable_caching=False, debug_mode=True)
        config = UnifiedConfig(features=features)

        assert config.is_feature_enabled("monitoring") is True
        assert config.is_feature_enabled("caching") is False
        assert config.is_feature_enabled("debug") is True
        assert config.is_feature_enabled("unknown") is False

    def test_validate_success(self):
        """Test successful configuration validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = UnifiedConfig(
                api_keys=APIKeysConfig(openai_api_key="valid-key-12345"),
                data_dir=Path(temp_dir) / "data",
                output_dir=Path(temp_dir) / "output",
                logs_dir=Path(temp_dir) / "logs",
            )

            # Should not raise an exception
            config.validate()

    def test_validate_invalid_port(self):
        """Test validation with invalid port."""
        config = UnifiedConfig()
        config.server.port = 99999  # Invalid port

        with pytest.raises(ConfigurationError, match="Invalid port number"):
            config.validate()

    def test_validate_invalid_workers(self):
        """Test validation with invalid workers count."""
        config = UnifiedConfig()
        config.server.workers = 0  # Invalid workers count

        with pytest.raises(ConfigurationError, match="Workers must be >= 1"):
            config.validate()

    def test_validate_missing_openai_key(self):
        """Test validation with missing OpenAI key."""
        config = UnifiedConfig(api_keys=APIKeysConfig(openai_api_key=""))

        with pytest.raises(ConfigurationError, match="OpenAI API key is required"):
            config.validate()

    def test_validate_short_openai_key(self):
        """Test validation with too short OpenAI key."""
        config = UnifiedConfig(api_keys=APIKeysConfig(openai_api_key="short"))

        with pytest.raises(ConfigurationError, match="OpenAI API key appears to be invalid"):
            config.validate()


class TestConfigFromEnvironment:
    """Test loading configuration from environment variables."""

    def test_from_env_minimal(self):
        """Test loading minimal configuration from environment."""
        env_vars = {"OPENAI_API_KEY": "test-openai-key-12345"}

        with patch.dict(os.environ, env_vars, clear=True):
            config = UnifiedConfig.from_env()

            assert config.api_keys.openai_api_key == "test-openai-key-12345"
            assert config.server.host == "0.0.0.0"  # Default
            assert config.server.port == 8000  # Default

    def test_from_env_full_config(self):
        """Test loading full configuration from environment."""
        env_vars = {
            "OPENAI_API_KEY": "test-openai-key-12345",
            "ANTHROPIC_API_KEY": "test-anthropic-key",
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "WORKERS": "4",
            "LOG_LEVEL": "DEBUG",
            "ENABLE_MONITORING": "false",
            "ENABLE_CACHING": "true",
            "DEBUG": "true",
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:8080",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = UnifiedConfig.from_env()

            # Server config
            assert config.server.host == "127.0.0.1"
            assert config.server.port == 9000
            assert config.server.workers == 4
            assert config.server.log_level == "DEBUG"

            # API keys
            assert config.api_keys.openai_api_key == "test-openai-key-12345"
            assert config.api_keys.anthropic_api_key == "test-anthropic-key"

            # Features
            assert config.features.enable_monitoring is False
            assert config.features.enable_caching is True
            assert config.features.debug_mode is True

            # Security
            assert config.security.cors_origins == ["http://localhost:3000", "http://localhost:8080"]

    def test_from_env_missing_required_key(self):
        """Test loading configuration with missing required API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError, match="OPENAI_API_KEY is required"):
                UnifiedConfig.from_env()

    def test_from_env_boolean_parsing(self):
        """Test boolean environment variable parsing."""
        env_vars = {
            "OPENAI_API_KEY": "test-key-12345",
            "ENABLE_MONITORING": "true",
            "ENABLE_CACHING": "false",
            "DEBUG": "True",
            "RELOAD": "FALSE",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = UnifiedConfig.from_env()

            assert config.features.enable_monitoring is True
            assert config.features.enable_caching is False
            assert config.features.debug_mode is True
            assert config.server.reload is False

    def test_from_env_integer_parsing(self):
        """Test integer environment variable parsing."""
        env_vars = {
            "OPENAI_API_KEY": "test-key-12345",
            "PORT": "9000",
            "WORKERS": "8",
            "CACHE_TTL": "7200",
            "RATE_LIMIT_REQUESTS": "200",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = UnifiedConfig.from_env()

            assert config.server.port == 9000
            assert config.server.workers == 8
            assert config.cache.default_ttl == 7200
            assert config.security.rate_limit_requests == 200


class TestGlobalConfigFunctions:
    """Test global configuration functions."""

    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_reload_config(self):
        """Test configuration reloading."""
        # Set up environment
        env_vars = {"OPENAI_API_KEY": "test-key-12345", "PORT": "8000"}

        with patch.dict(os.environ, env_vars, clear=True):
            config1 = get_config()
            original_port = config1.server.port

            # Change environment
            os.environ["PORT"] = "9000"

            # Reload config
            config2 = reload_config()

            # Should be a new instance with updated values
            assert config2 is not config1
            assert config2.server.port == 9000
            assert original_port == 8000


class TestConfigIntegration:
    """Integration tests for configuration system."""

    def test_config_with_temp_directories(self):
        """Test configuration with temporary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            env_vars = {
                "OPENAI_API_KEY": "test-key-12345",
                "DATA_DIR": str(temp_path / "data"),
                "OUTPUT_DIR": str(temp_path / "output"),
                "LOGS_DIR": str(temp_path / "logs"),
            }

            with patch.dict(os.environ, env_vars, clear=True):
                config = UnifiedConfig.from_env()

                # Directories should be created during validation
                config.validate()

                assert config.data_dir.exists()
                assert config.output_dir.exists()
                assert config.logs_dir.exists()

    def test_config_feature_integration(self):
        """Test feature flag integration."""
        env_vars = {
            "OPENAI_API_KEY": "test-key-12345",
            "ENABLE_MONITORING": "true",
            "ENABLE_CACHING": "true",
            "ENABLE_RESEARCH": "false",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = UnifiedConfig.from_env()

            # Test feature checking
            assert config.is_feature_enabled("monitoring") is True
            assert config.is_feature_enabled("caching") is True
            assert config.is_feature_enabled("research") is False
            assert config.is_feature_enabled("nonexistent") is False
