"""
Tests for Latency-Aware Policy Manager
"""

from starlink_security.policy_manager import (
    LatencyAwarePolicyManager,
    SecurityLevel,
    SecurityPolicy
)
from starlink_security.connection_monitor import ConnectionQuality, ConnectionMetrics
import time


def test_policy_manager_initialization():
    """Test policy manager initialization"""
    manager = LatencyAwarePolicyManager()
    assert len(manager._policies) == 5
    assert SecurityLevel.MAXIMUM in manager._policies


def test_default_policies():
    """Test default policy creation"""
    manager = LatencyAwarePolicyManager()
    
    # Check maximum security policy
    max_policy = manager._policies[SecurityLevel.MAXIMUM]
    assert max_policy.encryption_enabled is True
    assert max_policy.full_packet_inspection is True
    assert max_policy.log_verbosity == 5
    
    # Check emergency policy
    emergency_policy = manager._policies[SecurityLevel.EMERGENCY]
    assert emergency_policy.encryption_enabled is True  # Always enabled
    assert emergency_policy.full_packet_inspection is False
    assert emergency_policy.log_verbosity == 1


def test_policy_update_based_on_quality():
    """Test policy updates based on connection quality"""
    manager = LatencyAwarePolicyManager()
    
    # Test with excellent quality
    metrics = ConnectionMetrics(
        latency_ms=15.0,
        packet_loss_percent=0.05,
        bandwidth_mbps=200.0,
        jitter_ms=2.0,
        timestamp=time.time(),
        quality=ConnectionQuality.EXCELLENT
    )
    
    policy = manager.update_policy(metrics)
    assert policy.level == SecurityLevel.MAXIMUM
    assert policy.full_packet_inspection is True
    
    # Test with poor quality
    metrics.quality = ConnectionQuality.POOR
    policy = manager.update_policy(metrics)
    assert policy.level == SecurityLevel.LOW


def test_get_policy_for_quality():
    """Test getting policy for specific quality level"""
    manager = LatencyAwarePolicyManager()
    
    policy = manager.get_policy_for_quality(ConnectionQuality.GOOD)
    assert policy.level == SecurityLevel.HIGH


def test_feature_check():
    """Test feature enablement check"""
    manager = LatencyAwarePolicyManager()
    
    # Set high quality policy
    metrics = ConnectionMetrics(
        latency_ms=30.0,
        packet_loss_percent=0.3,
        bandwidth_mbps=150.0,
        jitter_ms=3.0,
        timestamp=time.time(),
        quality=ConnectionQuality.GOOD
    )
    manager.update_policy(metrics)
    
    assert manager.should_enable_feature('encryption') is True
    assert manager.should_enable_feature('packet_inspection') is True


def test_bandwidth_allowance():
    """Test bandwidth allowance calculation"""
    manager = LatencyAwarePolicyManager()
    
    metrics = ConnectionMetrics(
        latency_ms=45.0,
        packet_loss_percent=0.5,
        bandwidth_mbps=100.0,
        jitter_ms=5.0,
        timestamp=time.time(),
        quality=ConnectionQuality.GOOD
    )
    manager.update_policy(metrics)
    
    allowance = manager.get_bandwidth_allowance(100.0)
    assert allowance > 0
    assert allowance <= 100.0


def test_custom_policy():
    """Test setting custom policy"""
    manager = LatencyAwarePolicyManager()
    
    custom_policy = SecurityPolicy(
        level=SecurityLevel.MEDIUM,
        encryption_enabled=True,
        full_packet_inspection=False,
        log_verbosity=2,
        session_timeout_minutes=120,
        max_retry_attempts=3,
        bandwidth_limit_percent=8.0,
        cache_enabled=True,
        offline_mode_enabled=True
    )
    
    manager.set_custom_policy(ConnectionQuality.FAIR, custom_policy)
    policy = manager.get_policy_for_quality(ConnectionQuality.FAIR)
    assert policy.bandwidth_limit_percent == 8.0
