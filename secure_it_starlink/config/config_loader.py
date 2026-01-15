"""
Configuration management module with YAML-based configuration and deep merging support.
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigurationManager:
    """
    Manages YAML-based configuration with deep merging capabilities.
    
    Supports loading multiple configuration files with hierarchical merging,
    allowing for default configurations to be overridden by environment-specific
    or user-defined configurations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the primary configuration file.
                        If None, uses default config path.
        """
        self.config: Dict[str, Any] = {}
        self.config_path = config_path or self._get_default_config_path()
        self._load_configuration()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        base_dir = Path(__file__).parent.parent.parent
        return str(base_dir / "configs" / "default_config.yaml")
    
    def _load_configuration(self) -> None:
        """Load the primary configuration file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            # Initialize with empty config if file doesn't exist
            self.config = {}
    
    def deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Dictionary with override values
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self.deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value
        
        return result
    
    def load_and_merge(self, additional_config_path: str) -> None:
        """
        Load an additional configuration file and merge it with existing config.
        
        Args:
            additional_config_path: Path to additional configuration file
        """
        if not os.path.exists(additional_config_path):
            raise FileNotFoundError(f"Configuration file not found: {additional_config_path}")
        
        with open(additional_config_path, 'r') as f:
            additional_config = yaml.safe_load(f) or {}
        
        self.config = self.deep_merge(self.config, additional_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'metrics.security.weight')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration dictionary.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def save(self, output_path: Optional[str] = None) -> None:
        """
        Save the current configuration to a YAML file.
        
        Args:
            output_path: Path where to save the configuration.
                        If None, uses the original config_path.
        """
        path = output_path or self.config_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
