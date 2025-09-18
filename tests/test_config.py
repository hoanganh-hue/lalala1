"""
Unit tests for configuration management
"""
import pytest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config.settings import ConfigManager, config


class TestConfigManager:
    """Test ConfigManager class"""

    def test_config_singleton(self):
        """Test that config is a global instance"""
        assert isinstance(config, ConfigManager)

    def test_config_initialization(self):
        """Test config initialization"""
        config_obj = ConfigManager()
        assert config_obj is not None
        assert hasattr(config_obj, '_config')

    def test_get_api_config(self):
        """Test getting API configuration"""
        api_config = config.get_api_config()

        assert isinstance(api_config, dict)
        assert 'enterprise_url' in api_config
        assert 'vss_url' in api_config
        assert 'timeout' in api_config

    def test_get_processing_config(self):
        """Test getting processing configuration"""
        processing_config = config.get_processing_config()

        assert isinstance(processing_config, dict)
        assert 'max_workers' in processing_config
        assert 'batch_size' in processing_config

    def test_get_logging_config(self):
        """Test getting logging configuration"""
        logging_config = config.get_logging_config()

        assert isinstance(logging_config, dict)
        assert 'level' in logging_config
        assert 'file' in logging_config

    def test_get_default_values(self):
        """Test getting default configuration values"""
        # Test that we can access nested config values
        enterprise_url = config.get('api.enterprise_url')
        assert enterprise_url is not None
        assert isinstance(enterprise_url, str)

        max_workers = config.get('processing.max_workers')
        assert isinstance(max_workers, int)
        assert max_workers > 0

    def test_config_get_with_default(self):
        """Test config.get with default values"""
        # Test existing key
        existing_value = config.get('api.timeout', 10)
        assert existing_value == 45  # From default config

        # Test non-existing key with default
        default_value = config.get('non.existing.key', 'default')
        assert default_value == 'default'

    def test_config_file_loading(self):
        """Test loading configuration from file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"

            test_config = {
                "api": {
                    "timeout": 60,
                    "max_retries": 10
                },
                "processing": {
                    "max_workers": 8
                }
            }

            # Write test config
            config_file.write_text(json.dumps(test_config))

            # Create new config instance to test loading
            test_config_obj = ConfigManager(str(config_file))

            # Check values were loaded
            assert test_config_obj.get('api.timeout') == 60
            assert test_config_obj.get('api.max_retries') == 10
            assert test_config_obj.get('processing.max_workers') == 8

    def test_environment_variable_override(self):
        """Test environment variable override"""
        with patch.dict(os.environ, {'VSS_MAX_WORKERS': '16', 'VSS_LOG_LEVEL': 'DEBUG'}):
            # Create new config instance
            test_config = ConfigManager()
            test_config.update_from_env()

            assert test_config.get('processing.max_workers') == 16
            assert test_config.get('logging.level') == 'DEBUG'

    def test_config_validation(self):
        """Test configuration validation"""
        # Test that required fields exist
        api_config = config.get_api_config()
        assert 'enterprise_url' in api_config
        assert 'vss_url' in api_config

        processing_config = config.get_processing_config()
        assert 'max_workers' in processing_config
        assert 'batch_size' in processing_config

    def test_nested_config_access(self):
        """Test accessing nested configuration"""
        # Test deep nesting
        rate_limit = config.get('processing.rate_limit.max_requests_per_minute')
        assert isinstance(rate_limit, int)
        assert rate_limit > 0

        # Test security config
        user_agent = config.get('security.user_agent')
        assert isinstance(user_agent, str)
        assert len(user_agent) > 0

    def test_config_type_conversion(self):
        """Test configuration type conversion"""
        # Test integer conversion
        max_workers = config.get('processing.max_workers')
        assert isinstance(max_workers, int)

        # Test float conversion
        timeout = config.get('api.timeout')
        assert isinstance(timeout, (int, float))

        # Test boolean conversion
        cache_enabled = config.get('cache.enabled')
        assert isinstance(cache_enabled, bool)


class TestConfigErrorHandling:
    """Test configuration error handling"""

    def test_invalid_config_file(self):
        """Test handling invalid config file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "invalid_config.json"

            # Write invalid JSON
            config_file.write_text("invalid json content")

            test_config = ConfigManager(str(config_file))
            # Should not crash, should fall back to defaults
            assert test_config.get('api.timeout') == 45

    def test_missing_config_file(self):
        """Test handling missing config file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "missing_config.json"

            test_config = ConfigManager(str(config_file))
            # Should create default config and work
            assert test_config.get('api.timeout') == 45

    def test_invalid_environment_variables(self):
        """Test handling invalid environment variables"""
        with patch.dict(os.environ, {'VSS_MAX_WORKERS': 'invalid_number'}):
            test_config = ConfigManager()
            test_config.update_from_env()

            # Should fall back to default
            max_workers = test_config.get('processing.max_workers')
            assert isinstance(max_workers, int)
            assert max_workers > 0


if __name__ == "__main__":
    pytest.main([__file__])