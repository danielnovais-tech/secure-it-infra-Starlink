#!/usr/bin/env python3
"""
Tests for Starlink Security Foundation
"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from starlink_security import (
    StarlinkSecurityFoundation,
    NetworkMonitor,
    SecurityLevel,
    ConnectionType
)


def test_foundation_initialization():
    """Test that foundation initializes correctly."""
    foundation = StarlinkSecurityFoundation()
    assert foundation.security_level == SecurityLevel.NORMAL
    assert foundation.connection_type == ConnectionType.STARLINK_ONLY
    assert foundation.running is True
    assert foundation.metrics.security_score == 100
    print("✓ Foundation initialization test passed")


def test_security_report_generation():
    """Test security report generation."""
    foundation = StarlinkSecurityFoundation()
    report = foundation.get_security_report()
    
    assert "timestamp" in report
    assert "security_level" in report
    assert "connection_type" in report
    assert "metrics" in report
    assert "active_threats" in report
    assert "recommendations" in report
    
    # Verify report structure
    assert report["security_level"] == "normal"
    assert report["connection_type"] == "starlink_only"
    assert isinstance(report["active_threats"], list)
    assert isinstance(report["recommendations"], list)
    
    print("✓ Security report generation test passed")
    print(f"  Sample report: {json.dumps(report, indent=2)}")


async def test_event_triggering():
    """Test event triggering and logging."""
    foundation = StarlinkSecurityFoundation()
    
    # Trigger a test event
    await foundation.trigger_event(
        event_type="test_event",
        severity="info",
        source="test_suite",
        description="Test event description",
        metadata={"test_key": "test_value"}
    )
    
    # Check that event was queued
    assert not foundation.events_queue.empty()
    
    print("✓ Event triggering test passed")


def test_recommendations_generation():
    """Test that recommendations are generated based on metrics."""
    foundation = StarlinkSecurityFoundation()
    
    # Test with low security score
    foundation.metrics.security_score = 65
    recommendations = foundation._generate_recommendations()
    assert len(recommendations) > 0
    assert any("security monitoring" in rec.lower() for rec in recommendations)
    
    # Test with low connection stability
    foundation.metrics.security_score = 100
    foundation.metrics.connection_stability = 75
    recommendations = foundation._generate_recommendations()
    assert any("backup connection" in rec.lower() for rec in recommendations)
    
    # Test with active threats
    foundation.metrics.connection_stability = 100
    foundation.active_threats.add("test_threat")
    recommendations = foundation._generate_recommendations()
    assert any("threats" in rec.lower() for rec in recommendations)
    
    print("✓ Recommendations generation test passed")


def test_network_monitor_initialization():
    """Test network monitor initialization."""
    foundation = StarlinkSecurityFoundation()
    monitor = NetworkMonitor(foundation)
    
    assert monitor.foundation == foundation
    assert monitor.last_scan is None
    assert len(monitor.devices) == 0
    assert monitor.initialize()
    
    print("✓ Network monitor initialization test passed")


async def run_all_tests():
    """Run all tests."""
    print("Running Starlink Security Foundation Tests\n")
    print("=" * 50)
    
    # Synchronous tests
    test_foundation_initialization()
    test_security_report_generation()
    test_recommendations_generation()
    test_network_monitor_initialization()
    
    # Asynchronous tests
    await test_event_triggering()
    
    print("=" * 50)
    print("\nAll tests passed! ✓\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
