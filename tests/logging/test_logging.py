"""Tests for the security logging and alerting module."""

from secure_it_starlink.logging import (
    SecurityLogger, AlertManager, LogLevel, AlertSeverity
)


class TestSecurityLogger:
    """Test the SecurityLogger class."""

    def test_initialization(self):
        """Test logger initialization."""
        logger = SecurityLogger()
        assert len(logger.logs) == 0
        assert logger.min_level == LogLevel.INFO

    def test_log_info(self):
        """Test info level logging."""
        logger = SecurityLogger()
        entry = logger.info("Test message", {"key": "value"})
        
        assert entry["level"] == "INFO"
        assert entry["message"] == "Test message"
        assert entry["context"]["key"] == "value"
        assert "timestamp" in entry

    def test_log_warning(self):
        """Test warning level logging."""
        logger = SecurityLogger()
        entry = logger.warning("Warning message")
        
        assert entry["level"] == "WARNING"
        assert entry["message"] == "Warning message"

    def test_log_error(self):
        """Test error level logging."""
        logger = SecurityLogger()
        entry = logger.error("Error message")
        
        assert entry["level"] == "ERROR"
        assert entry["message"] == "Error message"

    def test_log_critical(self):
        """Test critical level logging."""
        logger = SecurityLogger()
        entry = logger.critical("Critical message")
        
        assert entry["level"] == "CRITICAL"
        assert entry["message"] == "Critical message"

    def test_log_debug(self):
        """Test debug level logging."""
        logger = SecurityLogger()
        entry = logger.debug("Debug message")
        
        assert entry["level"] == "DEBUG"
        assert entry["message"] == "Debug message"

    def test_get_logs(self):
        """Test getting logs."""
        logger = SecurityLogger()
        logger.info("Info 1")
        logger.warning("Warning 1")
        logger.error("Error 1")
        
        all_logs = logger.get_logs()
        assert len(all_logs) == 3
        
        # Test filtering by level
        error_logs = logger.get_logs(level=LogLevel.ERROR)
        assert len(error_logs) == 1
        assert error_logs[0]["level"] == "ERROR"
        
        # Test limit
        limited_logs = logger.get_logs(limit=2)
        assert len(limited_logs) == 2

    def test_clear_logs(self):
        """Test clearing logs."""
        logger = SecurityLogger()
        logger.info("Test")
        logger.warning("Test")
        
        assert len(logger.logs) == 2
        logger.clear_logs()
        assert len(logger.logs) == 0


class TestAlertManager:
    """Test the AlertManager class."""

    def test_initialization(self):
        """Test alert manager initialization."""
        manager = AlertManager()
        assert len(manager.alerts) == 0
        assert manager.active_alerts == 0

    def test_create_alert(self):
        """Test creating an alert."""
        manager = AlertManager()
        alert = manager.create_alert(
            AlertSeverity.HIGH,
            "Test Alert",
            "This is a test alert",
            {"key": "value"}
        )
        
        assert alert["severity"] == "HIGH"
        assert alert["title"] == "Test Alert"
        assert alert["description"] == "This is a test alert"
        assert alert["context"]["key"] == "value"
        assert alert["status"] == "active"
        assert alert["acknowledged"] is False
        assert "alert_id" in alert
        assert manager.active_alerts == 1

    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        manager = AlertManager()
        alert = manager.create_alert(
            AlertSeverity.MEDIUM,
            "Test",
            "Test"
        )
        
        result = manager.acknowledge_alert(alert["alert_id"])
        assert result is True
        
        # Verify acknowledgment
        alerts = manager.get_alerts()
        assert alerts[0]["acknowledged"] is True
        assert "acknowledged_at" in alerts[0]
        
        # Test acknowledging non-existent alert
        assert manager.acknowledge_alert("INVALID") is False

    def test_resolve_alert(self):
        """Test resolving an alert."""
        manager = AlertManager()
        alert = manager.create_alert(
            AlertSeverity.LOW,
            "Test",
            "Test"
        )
        
        result = manager.resolve_alert(alert["alert_id"], "Fixed the issue")
        assert result is True
        assert manager.active_alerts == 0
        
        # Verify resolution
        alerts = manager.get_alerts()
        assert alerts[0]["status"] == "resolved"
        assert alerts[0]["resolution"] == "Fixed the issue"
        assert "resolved_at" in alerts[0]
        
        # Test resolving non-existent alert
        assert manager.resolve_alert("INVALID") is False

    def test_get_alerts(self):
        """Test getting alerts."""
        manager = AlertManager()
        manager.create_alert(AlertSeverity.HIGH, "Alert 1", "Desc 1")
        manager.create_alert(AlertSeverity.CRITICAL, "Alert 2", "Desc 2")
        manager.create_alert(AlertSeverity.HIGH, "Alert 3", "Desc 3")
        
        # Get all alerts
        all_alerts = manager.get_alerts()
        assert len(all_alerts) == 3
        
        # Filter by severity
        high_alerts = manager.get_alerts(severity=AlertSeverity.HIGH)
        assert len(high_alerts) == 2
        
        # Filter by status
        manager.resolve_alert(all_alerts[0]["alert_id"])
        active_alerts = manager.get_alerts(status="active")
        assert len(active_alerts) == 2

    def test_get_active_alert_count(self):
        """Test getting active alert count."""
        manager = AlertManager()
        assert manager.get_active_alert_count() == 0
        
        alert1 = manager.create_alert(AlertSeverity.HIGH, "Test 1", "Desc 1")
        assert manager.get_active_alert_count() == 1
        
        manager.create_alert(AlertSeverity.MEDIUM, "Test 2", "Desc 2")
        assert manager.get_active_alert_count() == 2
        
        manager.resolve_alert(alert1["alert_id"])
        assert manager.get_active_alert_count() == 1

    def test_get_alert_stats(self):
        """Test getting alert statistics."""
        manager = AlertManager()
        manager.create_alert(AlertSeverity.CRITICAL, "Test 1", "Desc 1")
        manager.create_alert(AlertSeverity.HIGH, "Test 2", "Desc 2")
        manager.create_alert(AlertSeverity.HIGH, "Test 3", "Desc 3")
        
        stats = manager.get_alert_stats()
        assert stats["total_alerts"] == 3
        assert stats["active_alerts"] == 3
        assert stats["by_severity"]["CRITICAL"] == 1
        assert stats["by_severity"]["HIGH"] == 2
