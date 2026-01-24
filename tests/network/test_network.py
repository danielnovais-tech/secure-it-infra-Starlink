"""Tests for the network security monitoring module."""

from secure_it_starlink.network import NetworkMonitor, ConnectionValidator


class TestNetworkMonitor:
    """Test the NetworkMonitor class."""

    def test_initialization(self):
        """Test monitor initialization."""
        monitor = NetworkMonitor()
        assert monitor.monitoring_active is False
        assert len(monitor.connection_logs) == 0

    def test_start_monitoring(self):
        """Test starting network monitoring."""
        monitor = NetworkMonitor()
        monitor.start_monitoring()
        assert monitor.monitoring_active is True
        assert len(monitor.connection_logs) == 1
        assert monitor.connection_logs[0]["event"] == "monitoring_started"

    def test_stop_monitoring(self):
        """Test stopping network monitoring."""
        monitor = NetworkMonitor()
        monitor.start_monitoring()
        monitor.stop_monitoring()
        assert monitor.monitoring_active is False
        assert len(monitor.connection_logs) == 2
        assert monitor.connection_logs[1]["event"] == "monitoring_stopped"

    def test_check_connection_health(self):
        """Test connection health checking."""
        monitor = NetworkMonitor()
        health = monitor.check_connection_health("8.8.8.8")
        assert "timestamp" in health
        assert "target" in health
        assert health["target"] == "8.8.8.8"
        assert "status" in health
        assert "reachable" in health

    def test_get_connection_stats(self):
        """Test getting connection statistics."""
        monitor = NetworkMonitor()
        monitor.check_connection_health("8.8.8.8")
        stats = monitor.get_connection_stats()
        assert "total_checks" in stats
        assert "healthy_checks" in stats
        assert "unhealthy_checks" in stats
        assert "health_ratio" in stats
        assert stats["total_checks"] >= 0

    def test_get_logs(self):
        """Test getting connection logs."""
        monitor = NetworkMonitor()
        monitor.start_monitoring()
        monitor.check_connection_health("8.8.8.8")
        logs = monitor.get_logs()
        assert len(logs) >= 2
        
        # Test with limit
        limited_logs = monitor.get_logs(limit=1)
        assert len(limited_logs) == 1


class TestConnectionValidator:
    """Test the ConnectionValidator class."""

    def test_initialization(self):
        """Test validator initialization."""
        validator = ConnectionValidator()
        assert len(validator.allowed_networks) == 0
        assert len(validator.validation_logs) == 0

    def test_validate_connection(self):
        """Test connection validation."""
        validator = ConnectionValidator()
        result = validator.validate_connection("192.168.1.1", "example.com")
        assert "valid" in result
        assert "source_authorized" in result
        assert "destination_safe" in result
        assert "timestamp" in result

    def test_validate_invalid_ip(self):
        """Test validation with invalid IP."""
        validator = ConnectionValidator()
        result = validator.validate_connection("invalid.ip", "example.com")
        assert result["valid"] is False
        assert result["source_authorized"] is False

    def test_validate_suspicious_destination(self):
        """Test validation with suspicious destination."""
        validator = ConnectionValidator()
        result = validator.validate_connection("192.168.1.1", "localhost")
        assert result["valid"] is False
        assert result["destination_safe"] is False

    def test_add_allowed_network(self):
        """Test adding allowed networks."""
        validator = ConnectionValidator()
        validator.add_allowed_network("10.0.0.0/8")
        assert "10.0.0.0/8" in validator.allowed_networks
        
        # Test duplicate prevention
        validator.add_allowed_network("10.0.0.0/8")
        assert validator.allowed_networks.count("10.0.0.0/8") == 1

    def test_get_validation_logs(self):
        """Test getting validation logs."""
        validator = ConnectionValidator()
        validator.validate_connection("192.168.1.1", "example.com")
        validator.validate_connection("192.168.1.2", "test.com")
        
        logs = validator.get_validation_logs()
        assert len(logs) == 2
        
        # Test with limit
        limited_logs = validator.get_validation_logs(limit=1)
        assert len(limited_logs) == 1
