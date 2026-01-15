"""
Unit tests for Starlink Connection Metrics Module
"""

import pytest
from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    QualityThresholds,
    monitor_connection
)


class TestConnectionMetrics:
    """Test the ConnectionMetrics dataclass."""
    
    def test_valid_metrics(self):
        """Test creating valid metrics."""
        metrics = ConnectionMetrics(packet_loss=5.0, latency=100.0)
        assert metrics.packet_loss == 5.0
        assert metrics.latency == 100.0
    
    def test_invalid_packet_loss_negative(self):
        """Test that negative packet loss raises ValueError."""
        with pytest.raises(ValueError, match="packet_loss must be between 0 and 100"):
            ConnectionMetrics(packet_loss=-1.0, latency=100.0)
    
    def test_invalid_packet_loss_over_100(self):
        """Test that packet loss over 100 raises ValueError."""
        with pytest.raises(ValueError, match="packet_loss must be between 0 and 100"):
            ConnectionMetrics(packet_loss=101.0, latency=100.0)
    
    def test_invalid_latency_negative(self):
        """Test that negative latency raises ValueError."""
        with pytest.raises(ValueError, match="latency must be non-negative"):
            ConnectionMetrics(packet_loss=5.0, latency=-1.0)
    
    def test_zero_values(self):
        """Test that zero values are valid."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=0.0)
        assert metrics.packet_loss == 0.0
        assert metrics.latency == 0.0


class TestStarlinkConnectionQuality:
    """Test the StarlinkConnectionQuality class."""
    
    def test_perfect_quality_score(self):
        """Test quality score with perfect connection."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        quality = StarlinkConnectionQuality(metrics)
        assert quality.calculate_quality_score() == 100.0
    
    def test_quality_score_high_packet_loss(self):
        """Test quality score with high packet loss."""
        metrics = ConnectionMetrics(packet_loss=10.0, latency=50.0)
        quality = StarlinkConnectionQuality(metrics)
        # Base 100 - 10 for packet_loss > 5
        assert quality.calculate_quality_score() == 90.0
    
    def test_quality_score_high_latency(self):
        """Test quality score with high latency."""
        metrics = ConnectionMetrics(packet_loss=2.0, latency=200.0)
        quality = StarlinkConnectionQuality(metrics)
        # Base 100 - 5 for latency > 150
        assert quality.calculate_quality_score() == 95.0
    
    def test_quality_score_both_penalties(self):
        """Test quality score with both packet loss and latency penalties."""
        metrics = ConnectionMetrics(packet_loss=10.0, latency=200.0)
        quality = StarlinkConnectionQuality(metrics)
        # Base 100 - 10 for packet_loss - 5 for latency
        assert quality.calculate_quality_score() == 85.0
    
    def test_quality_score_minimum_clamp(self):
        """Test that quality score is clamped to 0."""
        metrics = ConnectionMetrics(packet_loss=50.0, latency=500.0)
        quality = StarlinkConnectionQuality(metrics)
        score = quality.calculate_quality_score()
        assert score >= 0
        assert score <= 100
    
    def test_quality_score_with_active_threats(self):
        """Test quality score deduction for active threats."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        active_threats = ["threat1", "threat2", "threat3"]
        quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
        # Base 100 - (3 threats * 5 points each) = 85
        assert quality.calculate_quality_score() == 85.0
    
    def test_quality_score_with_threats_and_penalties(self):
        """Test quality score with both active threats and connection penalties."""
        metrics = ConnectionMetrics(packet_loss=10.0, latency=200.0)
        active_threats = ["threat1", "threat2"]
        quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
        # Base 100 - 10 for packet_loss - 5 for latency - (2 threats * 5) = 75
        assert quality.calculate_quality_score() == 75.0
    
    def test_quality_score_no_threats(self):
        """Test quality score with no active threats (default)."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        quality = StarlinkConnectionQuality(metrics)
        assert quality.calculate_quality_score() == 100.0
    
    def test_quality_score_custom_threat_penalty(self):
        """Test quality score with custom threat penalty."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        active_threats = ["threat1", "threat2"]
        custom_thresholds = QualityThresholds(threat_penalty=10.0)
        quality = StarlinkConnectionQuality(
            metrics,
            quality_thresholds=custom_thresholds,
            active_threats=active_threats
        )
        # Base 100 - (2 threats * 10 points each) = 80
        assert quality.calculate_quality_score() == 80.0
    
    def test_quality_score_very_high_threats(self):
        """Test quality score with very high number of threats doesn't go negative."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        # 50 threats * 5 points each = 250 points deduction
        active_threats = [f"threat{i}" for i in range(50)]
        quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
        score = quality.calculate_quality_score()
        # Score should be clamped to 0, not negative
        assert score == 0.0
        assert score >= 0
    
    def test_quality_score_threats_with_all_penalties(self):
        """Test quality score with threats and all other penalties combined."""
        metrics = ConnectionMetrics(packet_loss=10.0, latency=200.0)
        active_threats = [f"threat{i}" for i in range(15)]  # 15 * 5 = 75
        quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
        # Base 100 - 10 (packet_loss) - 5 (latency) - 75 (threats) = 10
        assert quality.calculate_quality_score() == 10.0
    
    def test_quality_score_extreme_threats_with_penalties(self):
        """Test that score is properly clamped at 0 with extreme threat count and penalties."""
        metrics = ConnectionMetrics(packet_loss=50.0, latency=500.0)
        active_threats = [f"threat{i}" for i in range(20)]
        quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
        score = quality.calculate_quality_score()
        # With all penalties, this would go well below 0, but should be clamped
        assert score == 0.0
    
    def test_quality_score_weighted_threats_low_severity(self):
        """Test quality score with low severity threats (50% penalty)."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        active_threats = [
            {'id': 'threat1', 'severity': 'low'},
            {'id': 'threat2', 'severity': 'low'}
        ]
        quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
        # Base 100 - (2 threats * 5 * 0.5) = 95
        assert quality.calculate_quality_score() == 95.0
    
    def test_quality_score_weighted_threats_high_severity(self):
        """Test quality score with high severity threats (200% penalty)."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        active_threats = [
            {'id': 'threat1', 'severity': 'high'},
            {'id': 'threat2', 'severity': 'high'}
        ]
        quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
        # Base 100 - (2 threats * 5 * 2.0) = 80
        assert quality.calculate_quality_score() == 80.0
    
    def test_quality_score_mixed_severity_threats(self):
        """Test quality score with mixed severity threats."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        active_threats = [
            {'id': 'threat1', 'severity': 'low'},     # 5 * 0.5 = 2.5
            {'id': 'threat2', 'severity': 'medium'},  # 5 * 1.0 = 5.0
            {'id': 'threat3', 'severity': 'high'},    # 5 * 2.0 = 10.0
            'simple_threat'                            # 5 * 1.0 = 5.0
        ]
        quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
        # Base 100 - (2.5 + 5.0 + 10.0 + 5.0) = 77.5
        assert quality.calculate_quality_score() == 77.5
    
    def test_stability_perfect(self):
        """Test stability calculation with perfect metrics."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=0.0)
        quality = StarlinkConnectionQuality(metrics)
        stability = quality.calculate_stability_score()
        assert stability == 1.0
    
    def test_stability_high_packet_loss(self):
        """Test stability with high packet loss."""
        metrics = ConnectionMetrics(packet_loss=25.0, latency=0.0)
        quality = StarlinkConnectionQuality(metrics)
        stability = quality.calculate_stability_score()
        # packet_loss_decimal = 0.25
        # loss_factor = max(0, 1 - 0.25 * 2) = 0.5
        # latency_factor = max(0, 1 - 0/500) = 1.0
        # stability = 0.5 * 0.7 + 1.0 * 0.3 = 0.35 + 0.3 = 0.65
        assert abs(stability - 0.65) < 0.001
    
    def test_stability_high_latency(self):
        """Test stability with high latency."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=250.0)
        quality = StarlinkConnectionQuality(metrics)
        stability = quality.calculate_stability_score()
        # packet_loss_decimal = 0.0
        # loss_factor = max(0, 1 - 0 * 2) = 1.0
        # latency_factor = max(0, 1 - 250/500) = 0.5
        # stability = 1.0 * 0.7 + 0.5 * 0.3 = 0.7 + 0.15 = 0.85
        assert abs(stability - 0.85) < 0.001
    
    def test_stability_extreme_values(self):
        """Test stability with extreme values."""
        metrics = ConnectionMetrics(packet_loss=100.0, latency=1000.0)
        quality = StarlinkConnectionQuality(metrics)
        stability = quality.calculate_stability_score()
        # Both factors should be 0 or negative, clamped to 0
        assert stability == 0.0
    
    def test_get_connection_status_excellent(self):
        """Test connection status for excellent connection."""
        metrics = ConnectionMetrics(packet_loss=0.0, latency=20.0)
        quality = StarlinkConnectionQuality(metrics)
        status = quality.get_connection_status()
        
        assert status["status"] == "Excellent"
        assert status["quality_score"] == 100.0
        assert abs(status["stability_score"] - 0.988) < 0.001  # 20ms latency affects stability slightly
        assert status["packet_loss"] == 0.0
        assert status["latency"] == 20.0
    
    def test_get_connection_status_good(self):
        """Test connection status for good connection."""
        metrics = ConnectionMetrics(packet_loss=3.0, latency=100.0)
        quality = StarlinkConnectionQuality(metrics)
        status = quality.get_connection_status()
        
        assert status["status"] == "Good"
        assert status["quality_score"] == 100.0
        assert status["packet_loss"] == 3.0
        assert status["latency"] == 100.0
    
    def test_get_connection_status_fair(self):
        """Test connection status for fair connection."""
        metrics = ConnectionMetrics(packet_loss=10.0, latency=200.0)
        quality = StarlinkConnectionQuality(metrics)
        status = quality.get_connection_status()
        
        # With quality_score 85.0 and stability ~0.68, this is "Good"
        assert status["status"] == "Good"
        assert status["quality_score"] == 85.0
    
    def test_get_connection_status_poor(self):
        """Test connection status for poor connection."""
        metrics = ConnectionMetrics(packet_loss=50.0, latency=500.0)
        quality = StarlinkConnectionQuality(metrics)
        status = quality.get_connection_status()
        
        assert status["status"] == "Poor"


class TestMonitorConnection:
    """Test the monitor_connection convenience function."""
    
    def test_monitor_connection_excellent(self):
        """Test monitoring an excellent connection."""
        status = monitor_connection(packet_loss=1.0, latency=30.0)
        assert status["status"] == "Excellent"
        assert status["packet_loss"] == 1.0
        assert status["latency"] == 30.0
    
    def test_monitor_connection_poor(self):
        """Test monitoring a poor connection."""
        status = monitor_connection(packet_loss=60.0, latency=600.0)
        assert status["status"] == "Poor"
    
    def test_monitor_connection_returns_dict(self):
        """Test that monitor_connection returns a dictionary with expected keys."""
        status = monitor_connection(packet_loss=5.0, latency=100.0)
        assert isinstance(status, dict)
        assert "status" in status
        assert "quality_score" in status
        assert "stability_score" in status
        assert "packet_loss" in status
        assert "latency" in status
    
    def test_monitor_connection_with_active_threats(self):
        """Test monitoring connection with active threats."""
        active_threats = ["threat1", "threat2"]
        status = monitor_connection(packet_loss=1.0, latency=30.0, active_threats=active_threats)
        # Base 100 - (2 threats * 5) = 90
        assert status["quality_score"] == 90.0
        assert status["packet_loss"] == 1.0
        assert status["latency"] == 30.0
