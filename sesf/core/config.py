"""
SESF Configuration Management

Handles configuration loading, validation, and management for the framework.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class SESFConfig:
    """
    Configuration manager for SESF framework.
    
    Handles loading configuration from files and environment variables.
    """
    
    DEFAULT_CONFIG = {
        "framework": {
            "name": "SESF",
            "version": "1.0.0",
            "environment": "production"
        },
        "security": {
            "encryption_enabled": True,
            "encryption_algorithm": "AES-256-GCM",
            "tls_version": "1.3",
            "certificate_validation": True
        },
        "authentication": {
            "method": "multi-factor",
            "session_timeout": 3600,
            "max_login_attempts": 3
        },
        "network": {
            "firewall_enabled": True,
            "intrusion_detection": True,
            "rate_limiting": True,
            "allowed_protocols": ["HTTPS", "SSH", "Starlink-Proprietary"]
        },
        "monitoring": {
            "enabled": True,
            "log_level": "INFO",
            "alert_threshold": "HIGH",
            "metrics_collection": True
        },
        "compliance": {
            "standards": ["ISO27001", "SOC2", "NIST"],
            "audit_logging": True,
            "data_retention_days": 90
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (JSON)
        """
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
        
        self._load_from_env()
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            with open(file_path, 'r') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
            return True
        except Exception as e:
            print(f"Error loading config from {file_path}: {e}")
            return False
    
    def _load_from_env(self):
        """Load configuration overrides from environment variables."""
        env_prefix = "SESF_"
        
        # Check for common environment overrides
        if os.getenv(f"{env_prefix}ENVIRONMENT"):
            self.config["framework"]["environment"] = os.getenv(f"{env_prefix}ENVIRONMENT")
        
        if os.getenv(f"{env_prefix}LOG_LEVEL"):
            self.config["monitoring"]["log_level"] = os.getenv(f"{env_prefix}LOG_LEVEL")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """
        Merge new configuration with existing config.
        
        Args:
            new_config: New configuration dictionary to merge
        """
        for key, value in new_config.items():
            if key in self.config and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (dot notation supported, e.g., 'security.encryption_enabled')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get full configuration as dictionary.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save configuration to JSON file.
        
        Args:
            file_path: Path where to save configuration
            
        Returns:
            bool: True if saved successfully
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config to {file_path}: {e}")
            return False
