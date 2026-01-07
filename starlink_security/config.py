"""Configuration constants for Starlink Security."""

from pathlib import Path

# Directory constants
CONFIG_DIR = Path("/etc/starlink-security")
DATA_DIR = Path("/var/lib/starlink-security")
LOG_DIR = Path("/var/log/starlink-security")
"""
Configuration schemas and utilities for Starlink security infrastructure
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class StarlinkSecurityConfig:
    """Main configuration for Starlink security infrastructure"""
    
    # Connection Monitoring
    connection_check_interval: int = 30
    latency_threshold_excellent: float = 20.0
    latency_threshold_good: float = 50.0
    latency_threshold_fair: float = 100.0
    latency_threshold_poor: float = 200.0
    
    # Connection Resilience
    reconnect_attempts: int = 5
    reconnect_delay_seconds: int = 10
    failover_threshold_seconds: float = 30.0
    
    # Bandwidth Optimization
    bandwidth_limit_mbps: float = 100.0
    enable_compression: bool = True
    enable_caching: bool = True
    enable_deferred_ops: bool = True
    compression_level: str = "medium"  # none, low, medium, high, maximum
    
    # Remote Management
    management_mode: str = "supervised"  # autonomous, supervised, manual
    checkin_interval_minutes: int = 60
    autonomous_recovery: bool = True
    
    # Security Policies
    default_security_level: str = "high"  # maximum, high, medium, low, emergency
    enable_encryption: bool = True
    enable_packet_inspection: bool = True
    log_verbosity: int = 4  # 0-5 scale
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert configuration to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'StarlinkSecurityConfig':
        """Create configuration from dictionary"""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__})
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StarlinkSecurityConfig':
        """Create configuration from JSON string"""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'StarlinkSecurityConfig':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())


def create_default_config() -> StarlinkSecurityConfig:
    """Create default configuration"""
    return StarlinkSecurityConfig()


def create_remote_location_config() -> StarlinkSecurityConfig:
    """
    Create configuration optimized for remote, unmanned locations
    with emphasis on autonomy and resilience
    """
    return StarlinkSecurityConfig(
        # More frequent connection checks for remote locations
        connection_check_interval=60,
        
        # More aggressive reconnection
        reconnect_attempts=10,
        reconnect_delay_seconds=15,
        failover_threshold_seconds=45.0,
        
        # Conservative bandwidth usage
        bandwidth_limit_mbps=50.0,
        enable_compression=True,
        enable_caching=True,
        enable_deferred_ops=True,
        compression_level="high",
        
        # Autonomous operation
        management_mode="autonomous",
        checkin_interval_minutes=120,
        autonomous_recovery=True,
        
        # Balanced security for reliability
        default_security_level="medium",
        log_verbosity=3,
    )


def create_high_security_config() -> StarlinkSecurityConfig:
    """
    Create configuration with maximum security settings
    for critical infrastructure
    """
    return StarlinkSecurityConfig(
        # Frequent monitoring
        connection_check_interval=15,
        
        # Standard resilience
        reconnect_attempts=5,
        reconnect_delay_seconds=10,
        
        # Higher bandwidth allocation for security
        bandwidth_limit_mbps=150.0,
        compression_level="low",  # Less compression for faster processing
        
        # Supervised management
        management_mode="supervised",
        checkin_interval_minutes=30,
        
        # Maximum security
        default_security_level="maximum",
        enable_encryption=True,
        enable_packet_inspection=True,
        log_verbosity=5,
    )


def create_bandwidth_constrained_config() -> StarlinkSecurityConfig:
    """
    Create configuration optimized for severely bandwidth-constrained
    environments (e.g., shared Starlink connection)
    """
    return StarlinkSecurityConfig(
        # Less frequent checks to save bandwidth
        connection_check_interval=120,
        
        # Standard resilience
        reconnect_attempts=5,
        
        # Aggressive bandwidth optimization
        bandwidth_limit_mbps=25.0,
        enable_compression=True,
        enable_caching=True,
        enable_deferred_ops=True,
        compression_level="maximum",
        
        # Autonomous with minimal check-ins
        management_mode="autonomous",
        checkin_interval_minutes=240,
        
        # Reduced security overhead
        default_security_level="medium",
        enable_packet_inspection=False,
        log_verbosity=2,
    )
