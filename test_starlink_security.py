#!/usr/bin/env python3
"""
Tests for Starlink Security Foundation
"""

import asyncio
import pytest
from security import (
    SecurityLevel,
    StarlinkSecurityFoundation,
    NetworkMonitor,
    ThreatDetector,
    PolicyEnforcer
)


@pytest.mark.asyncio
async def test_network_monitor_initialization():
    """Test NetworkMonitor initialization."""
    foundation = StarlinkSecurityFoundation()
    monitor = NetworkMonitor(foundation)
    
    result = monitor.initialize()
    assert result is True
    assert len(monitor.devices) > 0
    assert "192.168.1.1" in monitor.devices


@pytest.mark.asyncio
async def test_unauthorized_device_detection():
    """Test detection of unauthorized devices."""
    foundation = StarlinkSecurityFoundation()
    monitor = NetworkMonitor(foundation)
    monitor.initialize()
    
    # Add an unauthorized device
    monitor.devices["192.168.1.100"] = {"trusted": False, "name": "Unknown"}
    
    events = []
    
    async def event_handler(event):
        events.append(event)
    
    foundation.event_handlers.append(event_handler)
    
    await monitor.scan_network()
    
    assert len(events) > 0
    assert events[0]['type'] == 'unauthorized_device_detected'
    assert '192.168.1.100' in events[0]['data']['unauthorized_devices']


@pytest.mark.asyncio
async def test_threat_detector_initialization():
    """Test ThreatDetector initialization."""
    foundation = StarlinkSecurityFoundation()
    detector = ThreatDetector(foundation)
    
    result = detector.initialize()
    assert result is True


@pytest.mark.asyncio
async def test_policy_enforcer_initialization():
    """Test PolicyEnforcer initialization."""
    foundation = StarlinkSecurityFoundation()
    enforcer = PolicyEnforcer(foundation)
    
    result = enforcer.initialize()
    assert result is True
    assert "network_access" in enforcer.active_policies
    assert "encryption" in enforcer.active_policies
    assert "authentication" in enforcer.active_policies


@pytest.mark.asyncio
async def test_security_level_application():
    """Test applying different security levels."""
    foundation = StarlinkSecurityFoundation()
    enforcer = PolicyEnforcer(foundation)
    enforcer.initialize()
    
    # Test CRITICAL level
    await enforcer.apply_security_level(SecurityLevel.CRITICAL)
    assert enforcer.active_policies["network_access"]["allowed_ports"] == [443]
    
    # Test ELEVATED level
    await enforcer.apply_security_level(SecurityLevel.ELEVATED)
    assert enforcer.active_policies["network_access"]["allowed_ports"] == [22, 443]


@pytest.mark.asyncio
async def test_event_triggering():
    """Test event triggering mechanism."""
    foundation = StarlinkSecurityFoundation()
    events = []
    
    async def event_handler(event):
        events.append(event)
    
    foundation.event_handlers.append(event_handler)
    
    await foundation.trigger_event(
        "test_event",
        "info",
        "test_source",
        "Test message",
        {"key": "value"}
    )
    
    assert len(events) == 1
    assert events[0]['type'] == 'test_event'
    assert events[0]['severity'] == 'info'
    assert events[0]['source'] == 'test_source'
    assert events[0]['data']['key'] == 'value'


@pytest.mark.asyncio
async def test_metrics_collection():
    """Test metrics collection functionality."""
    foundation = StarlinkSecurityFoundation()
    
    # Trigger some events
    await foundation.trigger_event("test_event_1", "info", "test", "Message 1")
    await foundation.trigger_event("test_event_2", "warning", "test", "Message 2")
    await foundation.trigger_event("test_event_1", "info", "test", "Message 3")
    
    metrics = foundation.get_metrics()
    
    assert 'event_counts' in metrics
    assert 'total_events' in metrics
    assert metrics['total_events'] >= 3
    assert 'test_event_1' in metrics['event_counts']
    assert metrics['event_counts']['test_event_1'] == 2


@pytest.mark.asyncio
async def test_policy_retrieval():
    """Test policy retrieval functionality."""
    foundation = StarlinkSecurityFoundation()
    enforcer = PolicyEnforcer(foundation)
    enforcer.initialize()
    
    policies = enforcer.get_policies()
    
    assert isinstance(policies, dict)
    assert "network_access" in policies
    assert "encryption" in policies
    assert "authentication" in policies


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
