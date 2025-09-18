"""
Centralized configuration settings for VSS Integration System
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from .default_config import DEFAULT_CONFIG


class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/settings.json"
        self._config = self._load_config()
        # Apply environment overrides immediately
        self.update_from_env()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                # Merge with defaults
                config = DEFAULT_CONFIG.copy()
                config.update(file_config)
                return config
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save config file {self.config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by key"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config(self._config)
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.get('api', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration"""
        return self.get('processing', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get('logging', {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration"""
        return self.get('cache', {})
    
    def update_from_env(self):
        """Update configuration from environment variables"""
        env_mappings = {
            'VSS_ENTERPRISE_API_URL': 'api.enterprise_url',
            'VSS_VSS_API_URL': 'api.vss_url',
            'VSS_REQUEST_TIMEOUT': 'api.timeout',
            'VSS_MAX_WORKERS': 'processing.max_workers',
            'VSS_BATCH_SIZE': 'processing.batch_size',
            'VSS_LOG_LEVEL': 'logging.level',
            'VSS_CACHE_TTL': 'cache.ttl',
            # API behavior
            'VSS_USE_MOCK_VSS': 'api.use_mock_vss',
            # Proxy configuration
            'VSS_ENABLE_PROXY': 'security.enable_proxy',
            'VSS_HTTP_PROXY': 'security.proxy_config.http',
            'VSS_HTTPS_PROXY': 'security.proxy_config.https'
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in ['api.timeout', 'processing.max_workers', 'processing.batch_size', 'cache.ttl']:
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                if config_key in ['security.enable_proxy', 'api.use_mock_vss']:
                    # Accept "true"/"false" strings
                    lowered = str(value).strip().lower()
                    if lowered in ['1', 'true', 'yes', 'on']:
                        value = True
                    elif lowered in ['0', 'false', 'no', 'off']:
                        value = False
                self.set(config_key, value)


# Global configuration instance
config = ConfigManager()
