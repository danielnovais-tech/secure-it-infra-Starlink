"""
Tests for Remote Manager Module
"""

import pytest
from datetime import datetime
from starlink_security.remote_manager import (
    RemoteManager,
    ManagementMode,
    AlertSeverity,
    RemoteAlert,
    HealthStatus
)


def test_remote_manager_initialization():
    """Test remote manager initialization"""
    manager = RemoteManager(
        mode=ManagementMode.SUPERVISED,
        checkin_interval_minutes=60,
        autonomous_recovery=True
    )
    
    assert manager.mode == ManagementMode.SUPERVISED
    assert manager.checkin_interval == 60
    assert manager.autonomous_recovery is True


def test_add_alert():
    """Test adding alerts"""
    manager = RemoteManager()
    
    alert = manager.add_alert(
        severity=AlertSeverity.WARNING,
        component="test_component",
        message="Test alert",
        auto_resolved=False
    )
    
    assert isinstance(alert, RemoteAlert)
    assert alert.severity == AlertSeverity.WARNING
    assert alert.message == "Test alert"


def test_get_alerts_filtering():
    """Test alert filtering"""
    manager = RemoteManager()
    
    manager.add_alert(AlertSeverity.INFO, "comp1", "Info msg", auto_resolved=True)
    manager.add_alert(AlertSeverity.WARNING, "comp2", "Warning msg", auto_resolved=False)
    manager.add_alert(AlertSeverity.CRITICAL, "comp3", "Critical msg", auto_resolved=False)
    
    # Get all alerts
    all_alerts = manager.get_alerts()
    assert len(all_alerts) == 3
    
    # Filter by severity
    warnings = manager.get_alerts(severity=AlertSeverity.WARNING)
    assert len(warnings) == 1
    assert warnings[0].severity == AlertSeverity.WARNING
    
    # Get only unresolved
    unresolved = manager.get_alerts(unresolved_only=True)
    assert len(unresolved) == 2


def test_clear_resolved_alerts():
    """Test clearing resolved alerts"""
    manager = RemoteManager()
    
    manager.add_alert(AlertSeverity.INFO, "comp1", "Msg1", auto_resolved=True)
    manager.add_alert(AlertSeverity.WARNING, "comp2", "Msg2", auto_resolved=False)
    
    cleared = manager.clear_resolved_alerts()
    assert cleared == 1
    assert len(manager.get_alerts()) == 1


def test_health_status_recording():
    """Test recording health status"""
    manager = RemoteManager()
    
    status = HealthStatus(
        timestamp=datetime.now(),
        overall_health="healthy",
        cpu_usage_percent=50.0,
        memory_usage_percent=60.0,
        disk_usage_percent=40.0,
        connection_quality="good",
        uptime_hours=24.0,
        alerts_count=0
    )
    
    manager.record_health_status(status)
    current = manager.get_current_health()
    
    assert current is not None
    assert current.overall_health == "healthy"


def test_queue_command():
    """Test queuing remote commands"""
    manager = RemoteManager()
    
    command = manager.queue_command(
        command_type="update_config",
        parameters={"key": "value"}
    )
    
    assert command.command_type == "update_config"
    assert command.status == "pending"
    assert command.parameters["key"] == "value"


def test_perform_checkin():
    """Test performing check-in"""
    manager = RemoteManager()
    
    # Add some data
    manager.add_alert(AlertSeverity.WARNING, "test", "msg")
    manager.queue_command("test_cmd", {})
    
    checkin_data = manager.perform_checkin()
    
    assert "timestamp" in checkin_data
    assert "mode" in checkin_data
    assert checkin_data["alerts_count"] > 0


def test_autonomous_mode():
    """Test enabling autonomous mode"""
    manager = RemoteManager(mode=ManagementMode.SUPERVISED)
    
    manager.enable_autonomous_mode()
    assert manager.mode == ManagementMode.AUTONOMOUS
    assert manager.autonomous_recovery is True


def test_configuration_cache():
    """Test configuration caching"""
    manager = RemoteManager()
    
    config = {"setting1": "value1", "setting2": "value2"}
    manager.update_configuration_cache(config)
    
    cached = manager.get_configuration_cache()
    assert cached["setting1"] == "value1"
    assert cached["setting2"] == "value2"
