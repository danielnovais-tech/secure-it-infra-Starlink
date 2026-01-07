"""Tests for the security monitor module."""
import pytest
import logging
from unittest.mock import patch, MagicMock
from src.security_monitor import SecurityMonitor


@pytest.fixture
def monitor():
    """Create a SecurityMonitor instance for testing."""
    return SecurityMonitor()


@pytest.fixture
def sample_metrics():
    """Sample security metrics for testing."""
    return {
        "failed_login_attempts": 3,
        "unauthorized_access_attempts": 0,
        "network_intrusion_attempts": 0,
        "active_connections": 150,
        "encrypted_connections": 145
    }


class TestSecurityMonitor:
    """Tests for SecurityMonitor class."""
    
    @pytest.mark.asyncio
    async def test_update_metrics_initial(self, monitor, sample_metrics):
        """Test updating metrics for the first time."""
        await monitor.update_metrics(sample_metrics)
        
        assert monitor.metrics == sample_metrics
        assert monitor.previous_metrics == {}
    
    @pytest.mark.asyncio
    async def test_update_metrics_with_previous(self, monitor, sample_metrics):
        """Test updating metrics when previous metrics exist."""
        # Set initial metrics
        await monitor.update_metrics(sample_metrics)
        
        # Update with new metrics
        new_metrics = sample_metrics.copy()
        new_metrics["failed_login_attempts"] = 5
        
        await monitor.update_metrics(new_metrics)
        
        assert monitor.metrics == new_metrics
        assert monitor.previous_metrics == sample_metrics
    
    @pytest.mark.asyncio
    async def test_update_metrics_error_handling(self, monitor):
        """Test error handling in update_metrics."""
        # This should not raise an exception
        with patch.object(monitor, '_log_significant_changes', side_effect=Exception("Test error")):
            await monitor.update_metrics({"test": "value"})
        
        # Metrics should still be updated despite the error
        assert monitor.metrics == {"test": "value"}
    
    def test_log_significant_changes_initial_metrics(self, monitor, caplog):
        """Test logging when no previous metrics exist."""
        monitor.metrics = {"failed_login_attempts": 3}
        
        with caplog.at_level(logging.INFO):
            monitor._log_significant_changes()
        
        assert "Initial metrics recorded" in caplog.text
    
    def test_log_significant_changes_numeric_change(self, monitor, caplog):
        """Test logging significant numeric changes."""
        monitor.previous_metrics = {"failed_login_attempts": 10}
        monitor.metrics = {"failed_login_attempts": 25}  # 150% change
        
        with caplog.at_level(logging.WARNING):
            monitor._log_significant_changes()
        
        assert "Significant change in failed_login_attempts" in caplog.text
        assert "150.0% change" in caplog.text
    
    def test_log_significant_changes_small_numeric_change(self, monitor, caplog):
        """Test that small numeric changes are not logged as significant."""
        monitor.previous_metrics = {"failed_login_attempts": 100}
        monitor.metrics = {"failed_login_attempts": 105}  # 5% change
        
        with caplog.at_level(logging.WARNING):
            monitor._log_significant_changes()
        
        # Should not log as significant (< 10% change)
        assert "Significant change" not in caplog.text
    
    def test_log_significant_changes_new_metric(self, monitor, caplog):
        """Test logging when a new metric is added."""
        monitor.previous_metrics = {"failed_login_attempts": 10}
        monitor.metrics = {
            "failed_login_attempts": 10,
            "new_metric": 5
        }
        
        with caplog.at_level(logging.INFO):
            monitor._log_significant_changes()
        
        assert "New metric added: new_metric = 5" in caplog.text
    
    def test_log_significant_changes_from_zero(self, monitor, caplog):
        """Test logging changes from zero value."""
        monitor.previous_metrics = {"failed_login_attempts": 0}
        monitor.metrics = {"failed_login_attempts": 5}
        
        with caplog.at_level(logging.WARNING):
            monitor._log_significant_changes()
        
        assert "Significant change in failed_login_attempts" in caplog.text
    
    def test_log_significant_changes_non_numeric(self, monitor, caplog):
        """Test logging non-numeric changes."""
        monitor.previous_metrics = {"status": "active"}
        monitor.metrics = {"status": "inactive"}
        
        with caplog.at_level(logging.INFO):
            monitor._log_significant_changes()
        
        assert "Change in status: active -> inactive" in caplog.text
    
    @pytest.mark.asyncio
    async def test_detect_anomalies_failed_logins(self, monitor, caplog):
        """Test anomaly detection for failed login attempts."""
        monitor.metrics = {"failed_login_attempts": 10}
        
        with caplog.at_level(logging.CRITICAL):
            await monitor._detect_anomalies()
        
        assert len(monitor.anomalies) == 1
        assert monitor.anomalies[0]["type"] == "authentication"
        assert monitor.anomalies[0]["severity"] == "high"
        assert "Anomaly detected" in caplog.text
    
    @pytest.mark.asyncio
    async def test_detect_anomalies_unauthorized_access(self, monitor, caplog):
        """Test anomaly detection for unauthorized access attempts."""
        monitor.metrics = {"unauthorized_access_attempts": 2}
        
        with caplog.at_level(logging.CRITICAL):
            await monitor._detect_anomalies()
        
        assert len(monitor.anomalies) == 1
        assert monitor.anomalies[0]["type"] == "access_control"
        assert monitor.anomalies[0]["severity"] == "critical"
    
    @pytest.mark.asyncio
    async def test_detect_anomalies_network_intrusion(self, monitor, caplog):
        """Test anomaly detection for network intrusion attempts."""
        monitor.metrics = {"network_intrusion_attempts": 1}
        
        with caplog.at_level(logging.CRITICAL):
            await monitor._detect_anomalies()
        
        assert len(monitor.anomalies) == 1
        assert monitor.anomalies[0]["type"] == "network_security"
        assert monitor.anomalies[0]["severity"] == "critical"
    
    @pytest.mark.asyncio
    async def test_detect_anomalies_multiple(self, monitor):
        """Test detection of multiple anomalies."""
        monitor.metrics = {
            "failed_login_attempts": 10,
            "unauthorized_access_attempts": 2,
            "network_intrusion_attempts": 1
        }
        
        await monitor._detect_anomalies()
        
        assert len(monitor.anomalies) == 3
    
    @pytest.mark.asyncio
    async def test_detect_anomalies_no_issues(self, monitor):
        """Test no anomalies when metrics are normal."""
        monitor.metrics = {
            "failed_login_attempts": 3,
            "unauthorized_access_attempts": 0,
            "network_intrusion_attempts": 0
        }
        
        await monitor._detect_anomalies()
        
        assert len(monitor.anomalies) == 0
    
    def test_calculate_security_score_perfect(self, monitor):
        """Test security score calculation with no issues."""
        monitor.metrics = {
            "failed_login_attempts": 0,
            "unauthorized_access_attempts": 0,
            "network_intrusion_attempts": 0
        }
        
        score = monitor._calculate_security_score()
        
        assert score == 100.0
    
    def test_calculate_security_score_failed_logins(self, monitor):
        """Test security score with failed login attempts."""
        monitor.metrics = {"failed_login_attempts": 5}
        
        score = monitor._calculate_security_score()
        
        # 5 failed logins * 2 points = 10 points deduction
        assert score == 90.0
    
    def test_calculate_security_score_unauthorized_access(self, monitor):
        """Test security score with unauthorized access attempts."""
        monitor.metrics = {"unauthorized_access_attempts": 2}
        
        score = monitor._calculate_security_score()
        
        # 2 unauthorized attempts * 10 points = 20 points deduction
        assert score == 80.0
    
    def test_calculate_security_score_network_intrusion(self, monitor):
        """Test security score with network intrusion attempts."""
        monitor.metrics = {"network_intrusion_attempts": 2}
        
        score = monitor._calculate_security_score()
        
        # 2 intrusion attempts * 15 points = 30 points deduction
        assert score == 70.0
    
    def test_calculate_security_score_with_anomalies(self, monitor):
        """Test security score considers anomalies."""
        monitor.metrics = {}
        monitor.anomalies = [
            {"severity": "critical"},
            {"severity": "critical"},
            {"severity": "high"}
        ]
        
        score = monitor._calculate_security_score()
        
        # 2 critical * 5 + 1 high * 2 = 12 points deduction
        assert score == 88.0
    
    def test_calculate_security_score_maximum_deductions(self, monitor):
        """Test security score with maximum deductions."""
        monitor.metrics = {
            "failed_login_attempts": 100,  # Capped at 20 points
            "unauthorized_access_attempts": 10,  # Capped at 30 points
            "network_intrusion_attempts": 10  # Capped at 40 points
        }
        
        score = monitor._calculate_security_score()
        
        # Should be capped at 20 + 30 + 40 = 90 points deduction
        assert score == 10.0
    
    def test_calculate_security_score_cannot_go_negative(self, monitor):
        """Test security score cannot go below zero."""
        monitor.metrics = {
            "failed_login_attempts": 100,
            "unauthorized_access_attempts": 100,
            "network_intrusion_attempts": 100
        }
        monitor.anomalies = [{"severity": "critical"} for _ in range(20)]
        
        score = monitor._calculate_security_score()
        
        assert score >= 0.0
    
    def test_get_security_score(self, monitor):
        """Test getting the security score."""
        monitor.metrics = {"failed_login_attempts": 5}
        
        score = monitor.get_security_score()
        
        assert score == 90.0
        assert monitor.security_score == 90.0
    
    @pytest.mark.asyncio
    async def test_get_anomalies_all(self, monitor):
        """Test getting all anomalies."""
        monitor.metrics = {
            "failed_login_attempts": 10,
            "unauthorized_access_attempts": 1
        }
        await monitor._detect_anomalies()
        
        anomalies = monitor.get_anomalies()
        
        assert len(anomalies) == 2
    
    @pytest.mark.asyncio
    async def test_get_anomalies_filtered_by_severity(self, monitor):
        """Test getting anomalies filtered by severity."""
        monitor.metrics = {
            "failed_login_attempts": 10,
            "unauthorized_access_attempts": 1
        }
        await monitor._detect_anomalies()
        
        critical_anomalies = monitor.get_anomalies(severity="critical")
        high_anomalies = monitor.get_anomalies(severity="high")
        
        assert len(critical_anomalies) == 1
        assert len(high_anomalies) == 1
    
    @pytest.mark.asyncio
    async def test_clear_anomalies(self, monitor, caplog):
        """Test clearing anomalies."""
        monitor.metrics = {"failed_login_attempts": 10}
        await monitor._detect_anomalies()
        
        assert len(monitor.anomalies) > 0
        
        with caplog.at_level(logging.INFO):
            monitor.clear_anomalies()
        
        assert len(monitor.anomalies) == 0
        assert "Anomalies cleared" in caplog.text
    
    @pytest.mark.asyncio
    async def test_integration_full_workflow(self, monitor, caplog):
        """Test the complete workflow of the security monitor."""
        # Initial metrics
        initial_metrics = {
            "failed_login_attempts": 2,
            "unauthorized_access_attempts": 0,
            "network_intrusion_attempts": 0
        }
        
        with caplog.at_level(logging.INFO):
            await monitor.update_metrics(initial_metrics)
        
        assert "Initial metrics recorded" in caplog.text
        assert len(monitor.anomalies) == 0
        
        # Update with problematic metrics
        caplog.clear()
        problematic_metrics = {
            "failed_login_attempts": 25,  # Significant increase
            "unauthorized_access_attempts": 2,
            "network_intrusion_attempts": 1
        }
        
        with caplog.at_level(logging.WARNING):
            await monitor.update_metrics(problematic_metrics)
        
        # Should log significant changes
        assert "Significant change in failed_login_attempts" in caplog.text
        
        # Should detect anomalies
        assert len(monitor.anomalies) == 3
        
        # Calculate security score
        score = monitor.get_security_score()
        
        # Score should be reduced due to issues
        assert score < 100.0
        
        # Clear anomalies
        monitor.clear_anomalies()
        assert len(monitor.anomalies) == 0
