"""
Tests for Connection Monitor Module
"""

import pytest
from starlink_security.connection_monitor import (
    ConnectionMonitor,
    ConnectionQuality,
    ConnectionMetrics
)


def test_connection_monitor_initialization():
    """Test connection monitor initialization"""
    monitor = ConnectionMonitor(check_interval=30)
    assert monitor.check_interval == 30
    assert monitor.thresholds['excellent'] == 20.0
    assert monitor.thresholds['good'] == 50.0


def test_connection_quality_determination():
    """Test connection quality determination logic"""
    monitor = ConnectionMonitor()
    
    # Test excellent quality
    quality = monitor._determine_quality(latency=15.0, packet_loss=0.05)
    assert quality == ConnectionQuality.EXCELLENT
    
    # Test good quality
    quality = monitor._determine_quality(latency=40.0, packet_loss=0.5)
    assert quality == ConnectionQuality.GOOD
    
    # Test fair quality
    quality = monitor._determine_quality(latency=80.0, packet_loss=2.0)
    assert quality == ConnectionQuality.FAIR
    
    # Test poor quality
    quality = monitor._determine_quality(latency=150.0, packet_loss=7.0)
    assert quality == ConnectionQuality.POOR
    
    # Test critical quality
    quality = monitor._determine_quality(latency=250.0, packet_loss=15.0)
    assert quality == ConnectionQuality.CRITICAL


def test_measure_connection():
    """Test connection measurement"""
    monitor = ConnectionMonitor()
    metrics = monitor.measure_connection()
    
    assert isinstance(metrics, ConnectionMetrics)
    assert metrics.latency_ms > 0
    assert metrics.bandwidth_mbps > 0
    assert isinstance(metrics.quality, ConnectionQuality)


def test_callback_registration():
    """Test callback registration and notification"""
    monitor = ConnectionMonitor()
    callback_called = [False]
    
    def test_callback(metrics):
        callback_called[0] = True
        assert isinstance(metrics, ConnectionMetrics)
    
    monitor.register_callback(test_callback)
    monitor.measure_connection()
    
    assert callback_called[0] is True


def test_connection_stability():
    """Test connection stability check"""
    monitor = ConnectionMonitor()
    monitor.measure_connection()
    
    # Should be stable at fair or better
    is_stable = monitor.is_connection_stable(ConnectionQuality.FAIR)
    assert isinstance(is_stable, bool)
    
    # With no metrics, should be False
    monitor._current_metrics = None
    is_stable = monitor.is_connection_stable()
    assert is_stable is False
