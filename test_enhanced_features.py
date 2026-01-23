"""
Unit tests for enhanced Starlink Connection Metrics features.

Tests for configurable thresholds, alert integration, service levels,
and historical smoothing functionality.
"""

import pytest
from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    QualityThresholds,
    StabilityThresholds,
    AlertThresholds,
    ServiceLevel
)


class TestConfigurableThresholds:
    """Test configurable thresholds functionality."""
    
    def test_custom_quality_thresholds(self):
        """Test using custom quality thresholds."""
        metrics = ConnectionMetrics(packet_loss=8.0, latency=180.0)
        custom_thresholds = QualityThresholds(
            packet_loss_threshold=10.0,  # More lenient
            packet_loss_penalty=15.0,
            latency_threshold=200.0,  # More lenient
            latency_penalty=8.0
        )
        quality = StarlinkConnectionQuality(
            metrics,
            quality_thresholds=custom_thresholds
        )
        
        # Should not trigger penalties with more lenient thresholds
        score = quality.calculate_quality_score()
        assert score == 100.0
    
    def test_quality_thresholds_validation(self):
        """Test QualityThresholds validation."""
        # Invalid packet loss threshold
        with pytest.raises(ValueError, match="packet_loss_threshold must be between 0 and 100"):
            QualityThresholds(packet_loss_threshold=150.0)
        
        # Negative penalty
        with pytest.raises(ValueError, match="packet_loss_penalty must be non-negative"):
            QualityThresholds(packet_loss_penalty=-5.0)
        
        # Negative latency threshold
        with pytest.raises(ValueError, match="latency_threshold must be non-negative"):
            QualityThresholds(latency_threshold=-100.0)
    
    def test_stability_thresholds_validation(self):
        """Test StabilityThresholds validation."""
        # Invalid weight range
        with pytest.raises(ValueError, match="packet_loss_weight must be between 0.0 and 1.0"):
            StabilityThresholds(packet_loss_weight=1.5, latency_weight=-0.5)
        
        # Weights don't sum to 1.0
        with pytest.raises(ValueError, match="must sum to 1.0"):
            StabilityThresholds(packet_loss_weight=0.6, latency_weight=0.6)
        
        # Negative max_latency
        with pytest.raises(ValueError, match="max_latency must be positive"):
            StabilityThresholds(max_latency=-500.0)
        
        # Negative multiplier
        with pytest.raises(ValueError, match="packet_loss_multiplier must be positive"):
            StabilityThresholds(packet_loss_multiplier=0)
    
    def test_alert_thresholds_validation(self):
        """Test AlertThresholds validation."""
        # Invalid range
        with pytest.raises(ValueError, match="critical_stability must be between 0.0 and 1.0"):
            AlertThresholds(critical_stability=1.5)
        
        # Thresholds not in ascending order
        with pytest.raises(ValueError, match="ascending order"):
            AlertThresholds(critical_stability=0.7, degraded_stability=0.5, stable_stability=0.3)
        
        # Equal thresholds
        with pytest.raises(ValueError, match="ascending order"):
            AlertThresholds(critical_stability=0.5, degraded_stability=0.5, stable_stability=0.7)
    
    def test_custom_stability_thresholds(self):
        """Test using custom stability thresholds."""
        metrics = ConnectionMetrics(packet_loss=10.0, latency=300.0)
        custom_stability = StabilityThresholds(
            max_latency=1000.0,  # Higher ceiling
            packet_loss_weight=0.5,  # Lower packet loss weight
            latency_weight=0.5,
            packet_loss_multiplier=1.5
        )
        quality = StarlinkConnectionQuality(
            metrics,
            stability_thresholds=custom_stability
        )
        
        stability = quality.calculate_stability_score()
        # With higher max_latency and lower packet_loss_weight, score should be higher
        assert stability > 0.5
    
    def test_default_thresholds_backward_compatibility(self):
        """Test that default thresholds maintain backward compatibility."""
        metrics = ConnectionMetrics(packet_loss=6.0, latency=160.0)
        quality = StarlinkConnectionQuality(metrics)
        
        # Should apply default penalties
        score = quality.calculate_quality_score()
        assert score == 85.0  # 100 - 10 (packet loss) - 5 (latency)


class TestServiceLevels:
    """Test service level classification."""
    
    def test_stable_service_level(self):
        """Test stable service level classification."""
        metrics = ConnectionMetrics(packet_loss=1.0, latency=50.0)
        quality = StarlinkConnectionQuality(metrics)
        stability = quality.calculate_stability_score()
        
        service_level = quality.get_service_level(stability)
        assert service_level == ServiceLevel.STABLE
    
    def test_degraded_service_level(self):
        """Test degraded service level classification."""
        metrics = ConnectionMetrics(packet_loss=20.0, latency=350.0)
        quality = StarlinkConnectionQuality(metrics)
        stability = quality.calculate_stability_score()
        
        service_level = quality.get_service_level(stability)
        assert service_level == ServiceLevel.DEGRADED
    
    def test_critical_service_level(self):
        """Test critical service level classification."""
        metrics = ConnectionMetrics(packet_loss=30.0, latency=400.0)
        quality = StarlinkConnectionQuality(metrics)
        stability = quality.calculate_stability_score()
        
        service_level = quality.get_service_level(stability)
        assert service_level == ServiceLevel.CRITICAL
    
    def test_offline_service_level(self):
        """Test offline service level classification."""
        metrics = ConnectionMetrics(packet_loss=60.0, latency=600.0)
        quality = StarlinkConnectionQuality(metrics)
        stability = quality.calculate_stability_score()
        
        service_level = quality.get_service_level(stability)
        assert service_level == ServiceLevel.OFFLINE
    
    def test_custom_alert_thresholds_for_service_levels(self):
        """Test custom alert thresholds affect service level mapping."""
        metrics = ConnectionMetrics(packet_loss=10.0, latency=200.0)
        custom_alerts = AlertThresholds(
            critical_stability=0.2,
            degraded_stability=0.4,
            stable_stability=0.6
        )
        quality = StarlinkConnectionQuality(
            metrics,
            alert_thresholds=custom_alerts
        )
        stability = quality.calculate_stability_score()
        service_level = quality.get_service_level(stability)
        
        # With adjusted thresholds, this might be STABLE instead of DEGRADED
        assert service_level in [ServiceLevel.STABLE, ServiceLevel.DEGRADED]


class TestAlertIntegration:
    """Test alert integration functionality."""
    
    def test_alert_callback_triggered_on_critical(self):
        """Test that alert callback is triggered when stability is critical."""
        alerts_received = []
        
        def alert_handler(level, data):
            alerts_received.append((level, data))
        
        metrics = ConnectionMetrics(packet_loss=40.0, latency=450.0)
        quality = StarlinkConnectionQuality(
            metrics,
            alert_callback=alert_handler
        )
        
        quality.get_connection_status()
        
        # Alert should have been triggered
        assert len(alerts_received) == 1
        assert alerts_received[0][0] == "critical"
        assert "stability" in alerts_received[0][1]
        assert "service_level" in alerts_received[0][1]
    
    def test_alert_callback_triggered_on_degraded(self):
        """Test that alert callback is triggered when stability is degraded."""
        alerts_received = []
        
        def alert_handler(level, data):
            alerts_received.append((level, data))
        
        metrics = ConnectionMetrics(packet_loss=22.0, latency=360.0)
        quality = StarlinkConnectionQuality(
            metrics,
            alert_callback=alert_handler
        )
        
        quality.get_connection_status()
        
        # Alert should have been triggered
        assert len(alerts_received) == 1
        assert alerts_received[0][0] == "degraded"
    
    def test_no_alert_when_stable(self):
        """Test that no alert is triggered when connection is stable."""
        alerts_received = []
        
        def alert_handler(level, data):
            alerts_received.append((level, data))
        
        metrics = ConnectionMetrics(packet_loss=2.0, latency=80.0)
        quality = StarlinkConnectionQuality(
            metrics,
            alert_callback=alert_handler
        )
        
        status = quality.get_connection_status()
        
        # No alert should be triggered
        assert len(alerts_received) == 0
        assert "alert_level" not in status
    
    def test_alert_level_in_status(self):
        """Test that alert level is included in status when triggered."""
        metrics = ConnectionMetrics(packet_loss=25.0, latency=380.0)
        quality = StarlinkConnectionQuality(metrics)
        
        status = quality.get_connection_status()
        
        assert "alert_level" in status
        assert status["alert_level"] in ["critical", "degraded"]


class TestHistoricalSmoothing:
    """Test historical tracking and smoothing functionality."""
    
    def test_history_disabled_by_default(self):
        """Test that history tracking is disabled by default."""
        metrics = ConnectionMetrics(packet_loss=5.0, latency=100.0)
        quality = StarlinkConnectionQuality(metrics)
        
        quality.calculate_stability_score()
        
        # History should be empty
        assert len(quality.stability_history) == 0
    
    def test_history_tracking_enabled(self):
        """Test that history tracking works when enabled."""
        quality = StarlinkConnectionQuality(
            ConnectionMetrics(packet_loss=5.0, latency=100.0),
            history_window_size=5
        )
        
        # Calculate stability multiple times
        for _ in range(3):
            quality.calculate_stability_score()
        
        # History should contain 3 entries
        assert len(quality.stability_history) == 3
    
    def test_history_window_size_limit(self):
        """Test that history respects window size limit."""
        quality = StarlinkConnectionQuality(
            ConnectionMetrics(packet_loss=5.0, latency=100.0),
            history_window_size=3
        )
        
        # Add more entries than window size
        for i in range(10):
            quality.calculate_stability_score()
        
        # History should only contain last 3 entries
        assert len(quality.stability_history) == 3
    
    def test_smoothing_averages_history(self):
        """Test that smoothing returns average of historical values."""
        quality = StarlinkConnectionQuality(
            ConnectionMetrics(packet_loss=5.0, latency=100.0),
            history_window_size=5
        )
        
        # Add first measurement
        first = quality.calculate_stability_score(use_smoothing=False)
        
        # Change metrics to create variation
        quality.metrics = ConnectionMetrics(packet_loss=10.0, latency=150.0)
        second = quality.calculate_stability_score(use_smoothing=False)
        
        # Get smoothed value (average of both)
        smoothed = quality.calculate_stability_score(use_smoothing=True)
        
        # Smoothed should be between the two values
        assert min(first, second) <= smoothed <= max(first, second)
    
    def test_history_size_in_status(self):
        """Test that history size is included in status when enabled."""
        quality = StarlinkConnectionQuality(
            ConnectionMetrics(packet_loss=5.0, latency=100.0),
            history_window_size=5
        )
        
        quality.calculate_stability_score()
        status = quality.get_connection_status()
        
        assert "stability_history_size" in status
        assert status["stability_history_size"] > 0


class TestEnhancedStatus:
    """Test enhanced connection status reporting."""
    
    def test_status_includes_service_level(self):
        """Test that connection status includes service level."""
        metrics = ConnectionMetrics(packet_loss=3.0, latency=90.0)
        quality = StarlinkConnectionQuality(metrics)
        
        status = quality.get_connection_status()
        
        assert "service_level" in status
        assert status["service_level"] in [sl.value for sl in ServiceLevel]
    
    def test_status_backward_compatible(self):
        """Test that status maintains backward compatibility."""
        metrics = ConnectionMetrics(packet_loss=5.0, latency=100.0)
        quality = StarlinkConnectionQuality(metrics)
        
        status = quality.get_connection_status()
        
        # All original fields should still be present
        assert "status" in status
        assert "quality_score" in status
        assert "stability_score" in status
        assert "packet_loss" in status
        assert "latency" in status
