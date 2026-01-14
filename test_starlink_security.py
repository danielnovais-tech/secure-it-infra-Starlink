#!/usr/bin/env python3
"""
Unit tests for Starlink Security Foundation
"""

import asyncio
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock
from starlink_security import (
    ConnectionType,
    SecurityLevel,
    SecurityMetrics,
    ThreatInfo,
    BackupConnectionManager,
    StarlinkSecurityFoundation
)


class TestConnectionType:
    """Test ConnectionType enum."""
    
    def test_connection_types(self):
        """Test that all connection types are defined."""
        assert ConnectionType.STARLINK_ONLY.value == "starlink_only"
        assert ConnectionType.FAILOVER.value == "failover"
        assert ConnectionType.DUAL_WAN.value == "dual_wan"
        assert ConnectionType.LOAD_BALANCED.value == "load_balanced"


class TestSecurityLevel:
    """Test SecurityLevel enum."""
    
    def test_security_levels(self):
        """Test that all security levels are defined."""
        assert SecurityLevel.MINIMAL.value == "minimal"
        assert SecurityLevel.LOW.value == "low"
        assert SecurityLevel.MODERATE.value == "moderate"
        assert SecurityLevel.HIGH.value == "high"
        assert SecurityLevel.CRITICAL.value == "critical"


class TestSecurityMetrics:
    """Test SecurityMetrics dataclass."""
    
    def test_default_values(self):
        """Test default metric values."""
        metrics = SecurityMetrics()
        assert metrics.security_score == 100.0
        assert metrics.connection_stability == 100.0
        assert metrics.packet_loss == 0.0
        assert metrics.latency == 0.0
        assert metrics.bandwidth_usage == 0.0
        assert metrics.threat_count == 0


class TestBackupConnectionManager:
    """Test BackupConnectionManager class."""
    
    @pytest.fixture
    def foundation(self):
        """Create a mock foundation for testing."""
        foundation = Mock(spec=StarlinkSecurityFoundation)
        foundation.metrics = SecurityMetrics()
        foundation.connection_type = ConnectionType.STARLINK_ONLY
        foundation.trigger_event = AsyncMock()
        return foundation
    
    def test_initialization(self, foundation):
        """Test backup manager initialization."""
        manager = BackupConnectionManager(foundation)
        assert manager.foundation == foundation
        assert len(manager.backup_connections) == 3
        assert "lte_backup" in manager.backup_connections
        assert "cable_backup" in manager.backup_connections
        assert "satellite_backup" in manager.backup_connections
        assert manager.active_backup is None
    
    @pytest.mark.asyncio
    async def test_activate_failover_success(self, foundation):
        """Test successful failover activation."""
        manager = BackupConnectionManager(foundation)
        
        await manager.activate_failover()
        
        assert manager.active_backup == "lte_backup"
        assert foundation.connection_type == ConnectionType.FAILOVER
        foundation.trigger_event.assert_called_once()
        
        # Verify the event was called with correct parameters
        call_args = foundation.trigger_event.call_args
        assert call_args[0][0] == "failover_activated"
        assert call_args[0][1] == "info"
    
    @pytest.mark.asyncio
    async def test_activate_failover_no_backup(self, foundation):
        """Test failover activation when no backups available."""
        manager = BackupConnectionManager(foundation)
        
        # Disable all backups
        for name in manager.backup_connections:
            manager.backup_connections[name]["available"] = False
        
        await manager.activate_failover()
        
        assert manager.active_backup is None
        foundation.trigger_event.assert_called_once()
        
        # Verify the event was called with correct parameters
        call_args = foundation.trigger_event.call_args
        assert call_args[0][0] == "failover_failed"
        assert call_args[0][1] == "critical"
    
    @pytest.mark.asyncio
    async def test_monitor_connection_triggers_failover(self, foundation):
        """Test that degraded connection triggers failover."""
        manager = BackupConnectionManager(foundation)
        
        # Set degraded metrics
        foundation.metrics.packet_loss = 15.0  # > 10
        
        await manager.monitor_connection()
        
        assert manager.active_backup == "lte_backup"
        assert foundation.connection_type == ConnectionType.FAILOVER
    
    @pytest.mark.asyncio
    async def test_monitor_connection_high_latency(self, foundation):
        """Test that high latency triggers failover."""
        manager = BackupConnectionManager(foundation)
        
        # Set high latency
        foundation.metrics.latency = 250.0  # > 200
        
        await manager.monitor_connection()
        
        assert manager.active_backup == "lte_backup"
        assert foundation.connection_type == ConnectionType.FAILOVER
    
    @pytest.mark.asyncio
    async def test_monitor_connection_low_stability(self, foundation):
        """Test that low stability triggers failover."""
        manager = BackupConnectionManager(foundation)
        
        # Set low stability
        foundation.metrics.connection_stability = 40.0  # < 50
        
        await manager.monitor_connection()
        
        assert manager.active_backup == "lte_backup"
        assert foundation.connection_type == ConnectionType.FAILOVER
    
    @pytest.mark.asyncio
    async def test_monitor_connection_no_failover_when_healthy(self, foundation):
        """Test that healthy connection does not trigger failover."""
        manager = BackupConnectionManager(foundation)
        
        # Set healthy metrics
        foundation.metrics.packet_loss = 5.0
        foundation.metrics.latency = 50.0
        foundation.metrics.connection_stability = 95.0
        
        await manager.monitor_connection()
        
        assert manager.active_backup is None
        assert foundation.connection_type == ConnectionType.STARLINK_ONLY


class TestStarlinkSecurityFoundation:
    """Test StarlinkSecurityFoundation class."""
    
    def test_initialization(self):
        """Test foundation initialization."""
        foundation = StarlinkSecurityFoundation()
        assert foundation.security_level == SecurityLevel.MINIMAL
        assert foundation.connection_type == ConnectionType.STARLINK_ONLY
        assert isinstance(foundation.metrics, SecurityMetrics)
        assert len(foundation.active_threats) == 0
        assert foundation.running is False
        assert isinstance(foundation.backup_manager, BackupConnectionManager)
    
    @pytest.mark.asyncio
    async def test_trigger_event(self):
        """Test event triggering."""
        foundation = StarlinkSecurityFoundation()
        
        await foundation.trigger_event(
            "test_event",
            "info",
            "test_source",
            "Test message",
            {"key": "value"}
        )
        
        assert len(foundation.events) == 1
        event = foundation.events[0]
        assert event["type"] == "test_event"
        assert event["severity"] == "info"
        assert event["source"] == "test_source"
        assert event["message"] == "Test message"
        assert event["metadata"] == {"key": "value"}
    
    def test_get_security_report(self):
        """Test security report generation."""
        foundation = StarlinkSecurityFoundation()
        
        report = foundation.get_security_report()
        
        assert "timestamp" in report
        assert report["security_level"] == "minimal"
        assert report["connection_type"] == "starlink_only"
        assert "metrics" in report
        assert "active_threats" in report
        assert "events" in report
        assert "backup_status" in report
    
    @pytest.mark.asyncio
    async def test_update_metrics(self):
        """Test metrics update."""
        foundation = StarlinkSecurityFoundation()
        
        await foundation.update_metrics()
        
        # Metrics should be updated (values will be random but within ranges)
        assert 0 <= foundation.metrics.packet_loss <= 15
        assert 10 <= foundation.metrics.latency <= 250
        assert 40 <= foundation.metrics.connection_stability <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
