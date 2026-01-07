"""
Configuration Security Scanner Module

Provides configuration validation and security scanning for
Starlink infrastructure configurations.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable


class ConfigScanner:
    """
    Scan and validate security configurations.
    
    Identifies misconfigurations and security issues in infrastructure
    configuration files.
    """

    def __init__(self):
        """Initialize the Configuration Scanner."""
        self.scan_results: List[Dict[str, Any]] = []
        self.rules: Dict[str, Callable[[Any], Dict[str, Any]]] = {}
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default security scanning rules."""
        self.add_rule("encryption_required", self._check_encryption_required)
        self.add_rule("strong_authentication", self._check_strong_authentication)
        self.add_rule("secure_protocols", self._check_secure_protocols)
        self.add_rule("network_segmentation", self._check_network_segmentation)

    def add_rule(self, rule_name: str, rule_func: Callable[[Any], Dict[str, Any]]) -> None:
        """
        Add a custom security scanning rule.
        
        Args:
            rule_name: Name of the rule
            rule_func: Function that takes config and returns check result
        """
        self.rules[rule_name] = rule_func

    def scan(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan a configuration for security issues.
        
        Args:
            config: Configuration dictionary to scan
            
        Returns:
            Scan results with findings
        """
        findings = []
        passed_checks = 0
        failed_checks = 0

        for rule_name, rule_func in self.rules.items():
            result = rule_func(config)
            result["rule_name"] = rule_name

            if result["passed"]:
                passed_checks += 1
            else:
                failed_checks += 1
                findings.append(result)

        scan_result = {
            "scan_id": f"CONFIG-SCAN-{len(self.scan_results) + 1:06d}",
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(self.rules),
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "findings": findings,
            "status": "completed"
        }

        self.scan_results.append(scan_result)
        return scan_result

    def _check_encryption_required(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if encryption is properly configured."""
        passed = config.get("encryption_enabled", False)
        return {
            "passed": passed,
            "severity": "CRITICAL" if not passed else "INFO",
            "message": "Encryption is required for all data transmission" if not passed else "Encryption is enabled",
            "recommendation": "Enable encryption_enabled in configuration" if not passed else None
        }

    def _check_strong_authentication(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check for strong authentication requirements."""
        auth_config = config.get("authentication", {})
        mfa_enabled = auth_config.get("mfa_enabled", False)
        min_password_length = auth_config.get("min_password_length", 0)

        passed = mfa_enabled and min_password_length >= 12

        return {
            "passed": passed,
            "severity": "HIGH" if not passed else "INFO",
            "message": "Strong authentication required" if not passed else "Strong authentication configured",
            "recommendation": "Enable MFA and set minimum password length to 12+" if not passed else None
        }

    def _check_secure_protocols(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check for secure protocol versions."""
        protocols = config.get("allowed_protocols", [])
        insecure_protocols = ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]

        has_insecure = any(proto in protocols for proto in insecure_protocols)

        return {
            "passed": not has_insecure,
            "severity": "HIGH" if has_insecure else "INFO",
            "message": "Insecure protocols detected" if has_insecure else "Only secure protocols configured",
            "recommendation": "Remove SSLv2, SSLv3, TLSv1.0, TLSv1.1 from allowed protocols" if has_insecure else None
        }

    def _check_network_segmentation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check for network segmentation configuration."""
        network_config = config.get("network", {})
        segmentation_enabled = network_config.get("segmentation_enabled", False)
        firewall_enabled = network_config.get("firewall_enabled", False)

        passed = segmentation_enabled and firewall_enabled

        return {
            "passed": passed,
            "severity": "MEDIUM" if not passed else "INFO",
            "message": "Network segmentation required" if not passed else "Network segmentation configured",
            "recommendation": "Enable network segmentation and firewall" if not passed else None
        }

    def get_scan_results(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get scan results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of scan results
        """
        if limit:
            return self.scan_results[-limit:]
        return self.scan_results.copy()


class SecurityConfig:
    """
    Manage security configuration settings.
    
    Provides a structured way to manage and validate security configurations.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Security Configuration.
        
        Args:
            config: Optional initial configuration
        """
        self.config = config or self._get_default_config()
        self.config_history: List[Dict[str, Any]] = []

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default security configuration."""
        return {
            "encryption_enabled": True,
            "cipher_suite": "AES-256-GCM",
            "authentication": {
                "mfa_enabled": True,
                "min_password_length": 12,
                "password_complexity": True,
                "session_timeout_minutes": 30
            },
            "allowed_protocols": ["TLSv1.2", "TLSv1.3"],
            "network": {
                "segmentation_enabled": True,
                "firewall_enabled": True,
                "intrusion_detection": True
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "retention_days": 90
            },
            "alerts": {
                "enabled": True,
                "critical_threshold": 3,
                "notification_channels": ["email", "sms"]
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        # Navigate to the parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Record old value
        old_value = config.get(keys[-1])

        # Set new value
        config[keys[-1]] = value

        # Record change in history
        self.config_history.append({
            "timestamp": datetime.now().isoformat(),
            "key": key,
            "old_value": old_value,
            "new_value": value
        })

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        for key, value in updates.items():
            self.set(key, value)

    def validate(self) -> Dict[str, Any]:
        """
        Validate the current configuration.
        
        Returns:
            Validation results
        """
        scanner = ConfigScanner()
        return scanner.scan(self.config)

    def get_config(self) -> Dict[str, Any]:
        """
        Get the full configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get configuration change history.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of configuration changes
        """
        if limit:
            return self.config_history[-limit:]
        return self.config_history.copy()

    def export_config(self) -> str:
        """
        Export configuration as a formatted string.
        
        Returns:
            Formatted configuration string
        """
        import json
        return json.dumps(self.config, indent=2)

    def load_config(self, config_str: str) -> None:
        """
        Load configuration from a JSON string.
        
        Args:
            config_str: JSON configuration string
        """
        import json
        self.config = json.loads(config_str)
"""Configuration package for Secure IT Starlink."""

from .config_loader import ConfigurationManager

__all__ = ["ConfigurationManager"]
