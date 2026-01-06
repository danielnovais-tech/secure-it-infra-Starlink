"""Tests for the configuration security scanner module."""

import pytest
from secure_it_starlink.config import ConfigScanner, SecurityConfig


class TestConfigScanner:
    """Test the ConfigScanner class."""

    def test_initialization(self):
        """Test scanner initialization."""
        scanner = ConfigScanner()
        assert len(scanner.scan_results) == 0
        assert len(scanner.rules) > 0

    def test_scan_secure_config(self):
        """Test scanning a secure configuration."""
        scanner = ConfigScanner()
        config = {
            "encryption_enabled": True,
            "authentication": {
                "mfa_enabled": True,
                "min_password_length": 12
            },
            "allowed_protocols": ["TLSv1.2", "TLSv1.3"],
            "network": {
                "segmentation_enabled": True,
                "firewall_enabled": True
            }
        }
        
        result = scanner.scan(config)
        
        assert result["status"] == "completed"
        assert result["failed_checks"] == 0
        assert len(result["findings"]) == 0

    def test_scan_insecure_config(self):
        """Test scanning an insecure configuration."""
        scanner = ConfigScanner()
        config = {
            "encryption_enabled": False,
            "authentication": {
                "mfa_enabled": False,
                "min_password_length": 8
            },
            "allowed_protocols": ["TLSv1.0", "SSLv3"],
            "network": {
                "segmentation_enabled": False,
                "firewall_enabled": False
            }
        }
        
        result = scanner.scan(config)
        
        assert result["failed_checks"] > 0
        assert len(result["findings"]) > 0

    def test_add_custom_rule(self):
        """Test adding a custom scanning rule."""
        scanner = ConfigScanner()
        
        def custom_rule(config):
            return {
                "passed": config.get("custom_setting", False),
                "severity": "MEDIUM",
                "message": "Custom check",
                "recommendation": "Enable custom setting"
            }
        
        scanner.add_rule("custom_check", custom_rule)
        assert "custom_check" in scanner.rules

    def test_get_scan_results(self):
        """Test getting scan results."""
        scanner = ConfigScanner()
        scanner.scan({"encryption_enabled": True})
        scanner.scan({"encryption_enabled": False})
        
        results = scanner.get_scan_results()
        assert len(results) == 2
        
        # Test with limit
        limited_results = scanner.get_scan_results(limit=1)
        assert len(limited_results) == 1


class TestSecurityConfig:
    """Test the SecurityConfig class."""

    def test_initialization(self):
        """Test security config initialization."""
        config = SecurityConfig()
        assert config.config is not None
        assert config.get("encryption_enabled") is True

    def test_initialization_with_custom_config(self):
        """Test initialization with custom configuration."""
        custom_config = {"test_key": "test_value"}
        config = SecurityConfig(custom_config)
        assert config.get("test_key") == "test_value"

    def test_get_value(self):
        """Test getting configuration values."""
        config = SecurityConfig()
        
        # Test simple key
        assert config.get("encryption_enabled") is True
        
        # Test nested key with dot notation
        assert config.get("authentication.mfa_enabled") is True
        
        # Test default value
        assert config.get("nonexistent", "default") == "default"

    def test_set_value(self):
        """Test setting configuration values."""
        config = SecurityConfig()
        
        # Set simple value
        config.set("new_key", "new_value")
        assert config.get("new_key") == "new_value"
        
        # Set nested value
        config.set("network.new_setting", True)
        assert config.get("network.new_setting") is True

    def test_update_values(self):
        """Test updating multiple values."""
        config = SecurityConfig()
        
        updates = {
            "encryption_enabled": False,
            "authentication.mfa_enabled": False
        }
        
        config.update(updates)
        
        assert config.get("encryption_enabled") is False
        assert config.get("authentication.mfa_enabled") is False

    def test_validate_config(self):
        """Test configuration validation."""
        config = SecurityConfig()
        
        result = config.validate()
        
        assert "total_checks" in result
        assert "passed_checks" in result
        assert "failed_checks" in result
        assert result["status"] == "completed"

    def test_get_config(self):
        """Test getting full configuration."""
        config = SecurityConfig()
        full_config = config.get_config()
        
        assert isinstance(full_config, dict)
        assert "encryption_enabled" in full_config

    def test_get_history(self):
        """Test getting configuration history."""
        config = SecurityConfig()
        
        config.set("test_key", "value1")
        config.set("test_key", "value2")
        
        history = config.get_history()
        assert len(history) == 2
        
        # Test with limit
        limited_history = config.get_history(limit=1)
        assert len(limited_history) == 1

    def test_export_config(self):
        """Test exporting configuration."""
        config = SecurityConfig()
        exported = config.export_config()
        
        assert isinstance(exported, str)
        assert "encryption_enabled" in exported

    def test_load_config(self):
        """Test loading configuration from string."""
        config = SecurityConfig()
        
        config_str = '{"test_key": "test_value", "encryption_enabled": false}'
        config.load_config(config_str)
        
        assert config.get("test_key") == "test_value"
        assert config.get("encryption_enabled") is False

    def test_default_config_values(self):
        """Test default configuration values."""
        config = SecurityConfig()
        
        assert config.get("encryption_enabled") is True
        assert config.get("cipher_suite") == "AES-256-GCM"
        assert config.get("authentication.mfa_enabled") is True
        assert config.get("network.firewall_enabled") is True
        assert config.get("logging.enabled") is True
