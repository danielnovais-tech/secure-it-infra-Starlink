"""
Latency-Aware Policy Manager

Dynamically adjusts security policies based on connection quality
to balance security requirements with operational constraints.
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
from .connection_monitor import ConnectionQuality, ConnectionMetrics


class SecurityLevel(Enum):
    """Security policy levels"""
    MAXIMUM = "maximum"      # Full security checks, maximum logging
    HIGH = "high"            # Standard security with full logging
    MEDIUM = "medium"        # Reduced logging, core security only
    LOW = "low"              # Minimal security, minimal logging
    EMERGENCY = "emergency"  # Bare minimum for operation


@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    level: SecurityLevel
    encryption_enabled: bool
    full_packet_inspection: bool
    log_verbosity: int  # 0-5 scale
    session_timeout_minutes: int
    max_retry_attempts: int
    bandwidth_limit_percent: float  # % of available bandwidth for security ops
    cache_enabled: bool
    offline_mode_enabled: bool


class LatencyAwarePolicyManager:
    """
    Manages security policies dynamically based on connection quality.
    Automatically adjusts security measures to maintain operations
    during degraded connectivity while maximizing security when possible.
    """
    
    def __init__(self):
        """Initialize policy manager with default policies"""
        self._policies = self._create_default_policies()
        self._current_policy: Optional[SecurityPolicy] = None
        self._quality_to_level_map = {
            ConnectionQuality.EXCELLENT: SecurityLevel.MAXIMUM,
            ConnectionQuality.GOOD: SecurityLevel.HIGH,
            ConnectionQuality.FAIR: SecurityLevel.MEDIUM,
            ConnectionQuality.POOR: SecurityLevel.LOW,
            ConnectionQuality.CRITICAL: SecurityLevel.EMERGENCY,
        }
    
    def _create_default_policies(self) -> Dict[SecurityLevel, SecurityPolicy]:
        """Create default security policies for each level"""
        return {
            SecurityLevel.MAXIMUM: SecurityPolicy(
                level=SecurityLevel.MAXIMUM,
                encryption_enabled=True,
                full_packet_inspection=True,
                log_verbosity=5,
                session_timeout_minutes=30,
                max_retry_attempts=5,
                bandwidth_limit_percent=15.0,
                cache_enabled=True,
                offline_mode_enabled=False,
            ),
            SecurityLevel.HIGH: SecurityPolicy(
                level=SecurityLevel.HIGH,
                encryption_enabled=True,
                full_packet_inspection=True,
                log_verbosity=4,
                session_timeout_minutes=45,
                max_retry_attempts=4,
                bandwidth_limit_percent=10.0,
                cache_enabled=True,
                offline_mode_enabled=False,
            ),
            SecurityLevel.MEDIUM: SecurityPolicy(
                level=SecurityLevel.MEDIUM,
                encryption_enabled=True,
                full_packet_inspection=False,
                log_verbosity=3,
                session_timeout_minutes=60,
                max_retry_attempts=3,
                bandwidth_limit_percent=5.0,
                cache_enabled=True,
                offline_mode_enabled=True,
            ),
            SecurityLevel.LOW: SecurityPolicy(
                level=SecurityLevel.LOW,
                encryption_enabled=True,
                full_packet_inspection=False,
                log_verbosity=2,
                session_timeout_minutes=90,
                max_retry_attempts=2,
                bandwidth_limit_percent=3.0,
                cache_enabled=True,
                offline_mode_enabled=True,
            ),
            SecurityLevel.EMERGENCY: SecurityPolicy(
                level=SecurityLevel.EMERGENCY,
                encryption_enabled=True,  # Always maintain encryption
                full_packet_inspection=False,
                log_verbosity=1,
                session_timeout_minutes=120,
                max_retry_attempts=1,
                bandwidth_limit_percent=1.0,
                cache_enabled=True,
                offline_mode_enabled=True,
            ),
        }
    
    def update_policy(self, metrics: ConnectionMetrics) -> SecurityPolicy:
        """
        Update security policy based on current connection metrics
        
        Args:
            metrics: Current connection metrics
            
        Returns:
            Updated security policy
        """
        target_level = self._quality_to_level_map[metrics.quality]
        self._current_policy = self._policies[target_level]
        return self._current_policy
    
    def get_current_policy(self) -> Optional[SecurityPolicy]:
        """Get the currently active security policy"""
        return self._current_policy
    
    def set_custom_policy(self, quality: ConnectionQuality, policy: SecurityPolicy) -> None:
        """
        Set a custom policy for a specific connection quality level
        
        Args:
            quality: Connection quality level
            policy: Custom security policy to apply
        """
        level = self._quality_to_level_map[quality]
        self._policies[level] = policy
    
    def get_policy_for_quality(self, quality: ConnectionQuality) -> SecurityPolicy:
        """
        Get the policy that would be applied for a given quality level
        
        Args:
            quality: Connection quality level
            
        Returns:
            Security policy for that quality level
        """
        level = self._quality_to_level_map[quality]
        return self._policies[level]
    
    def should_enable_feature(self, feature: str) -> bool:
        """
        Check if a specific security feature should be enabled
        based on current policy
        
        Args:
            feature: Feature name to check
            
        Returns:
            True if feature should be enabled
        """
        if not self._current_policy:
            return False
        
        feature_map = {
            'encryption': lambda p: p.encryption_enabled,
            'packet_inspection': lambda p: p.full_packet_inspection,
            'detailed_logging': lambda p: p.log_verbosity >= 4,
            'offline_mode': lambda p: p.offline_mode_enabled,
            'caching': lambda p: p.cache_enabled,
        }
        
        if feature in feature_map:
            return feature_map[feature](self._current_policy)
        
        return False
    
    def get_bandwidth_allowance(self, total_bandwidth_mbps: float) -> float:
        """
        Calculate bandwidth allowance for security operations
        
        Args:
            total_bandwidth_mbps: Total available bandwidth
            
        Returns:
            Bandwidth allocated for security operations in Mbps
        """
        if not self._current_policy:
            return total_bandwidth_mbps * 0.05  # Default 5%
        
        return total_bandwidth_mbps * (self._current_policy.bandwidth_limit_percent / 100.0)
