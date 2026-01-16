"""
Unit tests for Starlink Security Monitoring System
"""

import unittest
from unittest.mock import patch
import time
from starlink_monitor import StarlinkMonitor, SecurityMetrics


class TestSecurityMetrics(unittest.TestCase):
    """Test cases for SecurityMetrics data class."""
    
    def test_default_initialization(self):
        """Test that SecurityMetrics initializes with correct defaults."""
        metrics = SecurityMetrics()
        self.assertEqual(metrics.security_score, 0.0)
        self.assertEqual(metrics.connection_stability, 0.0)
        self.assertEqual(metrics.signal_quality, 100.0)
        self.assertEqual(metrics.latency_ms, 0.0)
        self.assertEqual(metrics.packet_loss_rate, 0.0)
        self.assertEqual(metrics.uptime_percentage, 100.0)
        self.assertEqual(metrics.failed_auth_attempts, 0)
        self.assertEqual(metrics.encryption_strength, 100.0)


class TestStarlinkMonitor(unittest.TestCase):
    """Test cases for StarlinkMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = StarlinkMonitor()
    
    def test_initialization(self):
        """Test that StarlinkMonitor initializes correctly."""
        self.assertIsNotNone(self.monitor.metrics)
        self.assertIsInstance(self.monitor.metrics, SecurityMetrics)
        self.assertGreater(self.monitor.metrics.last_updated, 0)
    
    def test_update_metrics(self):
        """Test updating individual metrics."""
        self.monitor.update_metrics(
            signal_quality=85.0,
            latency_ms=50.0,
            packet_loss_rate=1.5
        )
        
        self.assertEqual(self.monitor.metrics.signal_quality, 85.0)
        self.assertEqual(self.monitor.metrics.latency_ms, 50.0)
        self.assertEqual(self.monitor.metrics.packet_loss_rate, 1.5)
    
    def test_security_score_perfect_conditions(self):
        """Test security score calculation under perfect conditions."""
        self.monitor.update_metrics(
            encryption_strength=100.0,
            failed_auth_attempts=0,
            signal_quality=100.0,
            uptime_percentage=100.0,
            packet_loss_rate=0.0,
            latency_ms=20.0
        )
        
        # Perfect conditions should give a high security score
        self.assertGreaterEqual(self.monitor.metrics.security_score, 95.0)
        self.assertLessEqual(self.monitor.metrics.security_score, 100.0)
    
    def test_security_score_with_failed_auth(self):
        """Test security score decreases with failed auth attempts."""
        # First, set baseline
        self.monitor.update_metrics(
            encryption_strength=100.0,
            failed_auth_attempts=0,
            signal_quality=100.0,
            uptime_percentage=100.0,
            packet_loss_rate=0.0,
            latency_ms=20.0
        )
        baseline_score = self.monitor.metrics.security_score
        
        # Now add failed auth attempts
        self.monitor.update_metrics(
            encryption_strength=100.0,
            failed_auth_attempts=5,
            signal_quality=100.0,
            uptime_percentage=100.0,
            packet_loss_rate=0.0,
            latency_ms=20.0
        )
        
        # Score should be lower with failed auth attempts
        self.assertLess(self.monitor.metrics.security_score, baseline_score)
    
    def test_security_score_with_weak_encryption(self):
        """Test security score decreases with weak encryption."""
        self.monitor.update_metrics(
            encryption_strength=50.0,
            failed_auth_attempts=0,
            signal_quality=100.0,
            uptime_percentage=100.0,
            packet_loss_rate=0.0,
            latency_ms=20.0
        )
        
        # Weak encryption should significantly impact security score
        # Since encryption is 40% weight, score should be notably reduced
        self.assertLess(self.monitor.metrics.security_score, 80.0)
    
    def test_stability_perfect_conditions(self):
        """Test stability calculation under perfect conditions."""
        self.monitor.update_metrics(
            uptime_percentage=100.0,
            packet_loss_rate=0.0,
            signal_quality=100.0,
            latency_ms=20.0
        )
        
        # Perfect conditions should give a high stability score
        self.assertGreaterEqual(self.monitor.metrics.connection_stability, 95.0)
        self.assertLessEqual(self.monitor.metrics.connection_stability, 100.0)
    
    def test_stability_with_packet_loss(self):
        """Test stability decreases with packet loss."""
        # Baseline
        self.monitor.update_metrics(
            uptime_percentage=100.0,
            packet_loss_rate=0.0,
            signal_quality=100.0,
            latency_ms=20.0
        )
        baseline_stability = self.monitor.metrics.connection_stability
        
        # With packet loss
        self.monitor.update_metrics(
            uptime_percentage=100.0,
            packet_loss_rate=3.0,
            signal_quality=100.0,
            latency_ms=20.0
        )
        
        # Stability should be lower with packet loss
        self.assertLess(self.monitor.metrics.connection_stability, baseline_stability)
    
    def test_stability_with_high_latency(self):
        """Test stability decreases with high latency."""
        self.monitor.update_metrics(
            uptime_percentage=100.0,
            packet_loss_rate=0.0,
            signal_quality=100.0,
            latency_ms=300.0
        )
        
        # High latency should reduce stability
        self.assertLess(self.monitor.metrics.connection_stability, 95.0)
    
    def test_stability_with_low_uptime(self):
        """Test stability decreases with low uptime."""
        self.monitor.update_metrics(
            uptime_percentage=75.0,
            packet_loss_rate=0.0,
            signal_quality=100.0,
            latency_ms=20.0
        )
        
        # Lower uptime should reduce stability (uptime is 40% weight)
        self.assertLess(self.monitor.metrics.connection_stability, 90.0)
    
    def test_scores_bounded_to_valid_range(self):
        """Test that scores are always between 0 and 100."""
        # Test extreme bad conditions
        self.monitor.update_metrics(
            encryption_strength=0.0,
            failed_auth_attempts=100,
            signal_quality=0.0,
            uptime_percentage=0.0,
            packet_loss_rate=100.0,
            latency_ms=10000.0
        )
        
        self.assertGreaterEqual(self.monitor.metrics.security_score, 0.0)
        self.assertLessEqual(self.monitor.metrics.security_score, 100.0)
        self.assertGreaterEqual(self.monitor.metrics.connection_stability, 0.0)
        self.assertLessEqual(self.monitor.metrics.connection_stability, 100.0)
    
    def test_get_status_report(self):
        """Test that status report contains all expected metrics."""
        self.monitor.update_metrics(
            signal_quality=90.0,
            latency_ms=45.0,
            packet_loss_rate=1.0,
            uptime_percentage=99.5,
            failed_auth_attempts=2,
            encryption_strength=95.0
        )
        
        report = self.monitor.get_status_report()
        
        # Check all expected keys are present
        expected_keys = [
            'security_score',
            'connection_stability',
            'signal_quality',
            'latency_ms',
            'packet_loss_rate',
            'uptime_percentage',
            'failed_auth_attempts',
            'encryption_strength',
            'last_updated'
        ]
        
        for key in expected_keys:
            self.assertIn(key, report)
        
        # Verify values match
        self.assertEqual(report['signal_quality'], 90.0)
        self.assertEqual(report['latency_ms'], 45.0)
        self.assertEqual(report['packet_loss_rate'], 1.0)
    
    def test_metrics_update_timestamp(self):
        """Test that last_updated timestamp is updated on metric changes."""
        initial_timestamp = self.monitor.metrics.last_updated
        
        # Mock time.time to return a different value
        with patch('time.time', return_value=initial_timestamp + 100):
            self.monitor.update_metrics(signal_quality=95.0)
        
        self.assertGreater(self.monitor.metrics.last_updated, initial_timestamp)
        self.assertEqual(self.monitor.metrics.last_updated, initial_timestamp + 100)
    
    def test_realistic_scenario(self):
        """Test a realistic monitoring scenario."""
        # Simulate a typical good Starlink connection
        self.monitor.update_metrics(
            signal_quality=92.0,
            latency_ms=35.0,
            packet_loss_rate=0.5,
            uptime_percentage=99.0,
            failed_auth_attempts=1,
            encryption_strength=98.0
        )
        
        # Should have good scores for typical conditions
        self.assertGreater(self.monitor.metrics.security_score, 80.0)
        self.assertGreater(self.monitor.metrics.connection_stability, 85.0)


class TestCalculationMethods(unittest.TestCase):
    """Test specific calculation methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = StarlinkMonitor()
    
    def test_calculate_security_score_directly(self):
        """Test _calculate_security_score method directly."""
        self.monitor.metrics.encryption_strength = 100.0
        self.monitor.metrics.failed_auth_attempts = 0
        self.monitor.metrics.signal_quality = 100.0
        self.monitor.metrics.connection_stability = 100.0
        
        score = self.monitor._calculate_security_score()
        self.assertGreaterEqual(score, 95.0)
        self.assertLessEqual(score, 100.0)
    
    def test_calculate_stability_directly(self):
        """Test _calculate_stability method directly."""
        self.monitor.metrics.uptime_percentage = 100.0
        self.monitor.metrics.packet_loss_rate = 0.0
        self.monitor.metrics.signal_quality = 100.0
        self.monitor.metrics.latency_ms = 20.0
        
        stability = self.monitor._calculate_stability()
        self.assertGreaterEqual(stability, 95.0)
        self.assertLessEqual(stability, 100.0)


if __name__ == '__main__':
    unittest.main()
Tests for Starlink Network Monitoring System
"""
import pytest
from starlink_monitor import (
    StarlinkMonitor,
    NetworkMetrics,
    SecurityLevel
)


@pytest.fixture
def config():
    """Test configuration fixture."""
    return {
        'starlink': {
            'performance_thresholds': {
                'max_latency': 100.0,
                'max_jitter': 20.0,
                'max_packet_loss': 5.0,
                'min_throughput': 50.0
            }
        }
    }


@pytest.fixture
def monitor(config):
    """Create a monitor instance for testing."""
    return StarlinkMonitor(config)


class TestNetworkMetrics:
    """Test NetworkMetrics class."""
    
    def test_metrics_initialization(self):
        """Test that metrics initialize with default values."""
        metrics = NetworkMetrics()
        assert metrics.latency == 0.0
        assert metrics.jitter == 0.0
        assert metrics.packet_loss == 0.0
        assert metrics.throughput == 0.0
        assert metrics.security_score == 100.0
    
    def test_metrics_dict(self):
        """Test metrics dictionary conversion."""
        metrics = NetworkMetrics(
            latency=50.0,
            jitter=10.0,
            packet_loss=2.0,
            throughput=100.0,
            security_score=85.0
        )
        metrics_dict = metrics.to_dict()
        assert metrics_dict['latency'] == 50.0
        assert metrics_dict['jitter'] == 10.0
        assert metrics_dict['packet_loss'] == 2.0
        assert metrics_dict['throughput'] == 100.0
        assert metrics_dict['security_score'] == 85.0


class TestStabilityCalculation:
    """Test stability calculation functionality."""
    
    def test_perfect_stability(self, monitor):
        """Test stability with no jitter or packet loss."""
        monitor.metrics = NetworkMetrics(jitter=0.0, packet_loss=0.0)
        stability = monitor.calculate_stability()
        assert stability == 100.0
    
    def test_jitter_deduction(self, monitor):
        """Test that jitter reduces stability."""
        monitor.metrics = NetworkMetrics(jitter=10.0, packet_loss=0.0)
        stability = monitor.calculate_stability()
        # Jitter deduction: min(10 * 2, 30) = 20
        assert stability == 80.0
    
    def test_jitter_deduction_capped(self, monitor):
        """Test that jitter deduction is capped at 30."""
        monitor.metrics = NetworkMetrics(jitter=20.0, packet_loss=0.0)
        stability = monitor.calculate_stability()
        # Jitter deduction: min(20 * 2, 30) = 30
        assert stability == 70.0
    
    def test_packet_loss_deduction(self, monitor):
        """Test that packet loss reduces stability."""
        monitor.metrics = NetworkMetrics(jitter=0.0, packet_loss=2.0)
        stability = monitor.calculate_stability()
        # Packet loss deduction: min(2 * 10, 40) = 20
        assert stability == 80.0
    
    def test_packet_loss_deduction_capped(self, monitor):
        """Test that packet loss deduction is capped at 40."""
        monitor.metrics = NetworkMetrics(jitter=0.0, packet_loss=5.0)
        stability = monitor.calculate_stability()
        # Packet loss deduction: min(5 * 10, 40) = 40
        assert stability == 60.0
    
    def test_combined_deductions(self, monitor):
        """Test combined jitter and packet loss deductions."""
        monitor.metrics = NetworkMetrics(jitter=10.0, packet_loss=3.0)
        stability = monitor.calculate_stability()
        # Jitter: min(10 * 2, 30) = 20
        # Packet loss: min(3 * 10, 40) = 30
        # Total deduction: 50
        assert stability == 50.0
    
    def test_stability_floor(self, monitor):
        """Test that stability cannot go below 0."""
        monitor.metrics = NetworkMetrics(jitter=50.0, packet_loss=10.0)
        stability = monitor.calculate_stability()
        # Jitter: min(50 * 2, 30) = 30
        # Packet loss: min(10 * 10, 40) = 40
        # Total: 100 - 30 - 40 = 30
        assert stability == 30.0
    
    def test_stability_ceiling(self, monitor):
        """Test that stability cannot exceed 100."""
        monitor.metrics = NetworkMetrics(jitter=0.0, packet_loss=0.0)
        stability = monitor.calculate_stability()
        assert stability <= 100.0


class TestAnomalyDetection:
    """Test anomaly detection functionality."""
    
    @pytest.mark.asyncio
    async def test_high_latency_anomaly(self, monitor):
        """Test detection of high latency."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(
            latency=150.0,  # Above threshold of 100
            jitter=5.0,
            packet_loss=1.0,
            throughput=100.0
        )
        
        await monitor._detect_anomalies()
        
        assert len(events) == 1
        assert events[0]['type'] == 'network_anomaly_detected'
        assert events[0]['severity'] == 'warning'
        assert 'High latency: 150.0ms' in events[0]['data']['anomalies']
    
    @pytest.mark.asyncio
    async def test_high_jitter_anomaly(self, monitor):
        """Test detection of high jitter."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(
            latency=50.0,
            jitter=25.0,  # Above threshold of 20
            packet_loss=1.0,
            throughput=100.0
        )
        
        await monitor._detect_anomalies()
        
        assert len(events) == 1
        assert 'High jitter: 25.0ms' in events[0]['data']['anomalies']
    
    @pytest.mark.asyncio
    async def test_high_packet_loss_anomaly(self, monitor):
        """Test detection of high packet loss."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(
            latency=50.0,
            jitter=5.0,
            packet_loss=10.0,  # Above threshold of 5
            throughput=100.0
        )
        
        await monitor._detect_anomalies()
        
        assert len(events) == 1
        assert 'High packet loss: 10.0%' in events[0]['data']['anomalies']
    
    @pytest.mark.asyncio
    async def test_low_throughput_anomaly(self, monitor):
        """Test detection of low throughput."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(
            latency=50.0,
            jitter=5.0,
            packet_loss=1.0,
            throughput=30.0  # Below threshold of 50
        )
        
        await monitor._detect_anomalies()
        
        assert len(events) == 1
        assert 'Low throughput: 30.0Mbps' in events[0]['data']['anomalies']
    
    @pytest.mark.asyncio
    async def test_multiple_anomalies(self, monitor):
        """Test detection of multiple anomalies."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(
            latency=150.0,  # High
            jitter=25.0,    # High
            packet_loss=10.0,  # High
            throughput=30.0    # Low
        )
        
        await monitor._detect_anomalies()
        
        assert len(events) == 1
        anomalies = events[0]['data']['anomalies']
        assert len(anomalies) == 4
        assert any('High latency' in a for a in anomalies)
        assert any('High jitter' in a for a in anomalies)
        assert any('High packet loss' in a for a in anomalies)
        assert any('Low throughput' in a for a in anomalies)
    
    @pytest.mark.asyncio
    async def test_no_anomalies(self, monitor):
        """Test when no anomalies are detected."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(
            latency=50.0,
            jitter=10.0,
            packet_loss=2.0,
            throughput=100.0
        )
        
        await monitor._detect_anomalies()
        
        assert len(events) == 0


class TestSecurityStatus:
    """Test security status checking functionality."""
    
    @pytest.mark.asyncio
    async def test_normal_security_level(self, monitor):
        """Test normal security level."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(security_score=80.0)
        monitor.security_level = SecurityLevel.ELEVATED
        
        await monitor._check_security_status()
        
        assert monitor.security_level == SecurityLevel.NORMAL
        assert len(events) == 1
        assert events[0]['type'] == 'security_level_changed'
        assert events[0]['data']['old_level'] == 'elevated'
        assert events[0]['data']['new_level'] == 'normal'
    
    @pytest.mark.asyncio
    async def test_elevated_security_level(self, monitor):
        """Test elevated security level."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(security_score=60.0)
        
        await monitor._check_security_status()
        
        assert monitor.security_level == SecurityLevel.ELEVATED
        assert len(events) == 1
        assert events[0]['data']['new_level'] == 'elevated'
    
    @pytest.mark.asyncio
    async def test_critical_security_level(self, monitor):
        """Test critical security level."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(security_score=40.0)
        
        await monitor._check_security_status()
        
        assert monitor.security_level == SecurityLevel.CRITICAL
        assert len(events) == 1
        assert events[0]['data']['new_level'] == 'critical'
    
    @pytest.mark.asyncio
    async def test_no_level_change(self, monitor):
        """Test when security level doesn't change."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(security_score=80.0)
        monitor.security_level = SecurityLevel.NORMAL
        
        await monitor._check_security_status()
        
        assert monitor.security_level == SecurityLevel.NORMAL
        assert len(events) == 0  # No event should be triggered
    
    @pytest.mark.asyncio
    async def test_boundary_conditions(self, monitor):
        """Test boundary conditions for security levels."""
        # Test at 70 (should be NORMAL)
        monitor.metrics = NetworkMetrics(security_score=70.0)
        await monitor._check_security_status()
        assert monitor.security_level == SecurityLevel.NORMAL
        
        # Test at 69.9 (should be ELEVATED)
        monitor.security_level = SecurityLevel.NORMAL  # Reset
        monitor.metrics = NetworkMetrics(security_score=69.9)
        await monitor._check_security_status()
        assert monitor.security_level == SecurityLevel.ELEVATED
        
        # Test at 50 (should be ELEVATED)
        monitor.security_level = SecurityLevel.NORMAL  # Reset
        monitor.metrics = NetworkMetrics(security_score=50.0)
        await monitor._check_security_status()
        assert monitor.security_level == SecurityLevel.ELEVATED
        
        # Test at 49.9 (should be CRITICAL)
        monitor.security_level = SecurityLevel.NORMAL  # Reset
        monitor.metrics = NetworkMetrics(security_score=49.9)
        await monitor._check_security_status()
        assert monitor.security_level == SecurityLevel.CRITICAL


class TestMonitorIntegration:
    """Integration tests for the monitor."""
    
    @pytest.mark.asyncio
    async def test_monitor_loop(self, monitor):
        """Test the main monitoring loop."""
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        monitor.event_handlers.append(event_handler)
        monitor.metrics = NetworkMetrics(
            latency=150.0,
            jitter=25.0,
            packet_loss=10.0,
            throughput=30.0,
            security_score=40.0
        )
        
        await monitor.monitor()
        
        # Should trigger both anomaly and security events
        assert len(events) == 2
        event_types = [e['type'] for e in events]
        assert 'network_anomaly_detected' in event_types
        assert 'security_level_changed' in event_types
    
    def test_update_metrics(self, monitor):
        """Test updating metrics."""
        new_metrics = NetworkMetrics(
            latency=75.0,
            jitter=12.0,
            packet_loss=3.0,
            throughput=80.0,
            security_score=85.0
        )
        
        monitor.update_metrics(new_metrics)
        
        assert monitor.metrics.latency == 75.0
        assert monitor.metrics.jitter == 12.0
        assert monitor.metrics.packet_loss == 3.0
        assert monitor.metrics.throughput == 80.0
        assert monitor.metrics.security_score == 85.0
    
    @pytest.mark.asyncio
    async def test_missing_config_validation(self):
        """Test that monitor handles missing configuration gracefully."""
        # Test with empty config
        empty_monitor = StarlinkMonitor({})
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        empty_monitor.event_handlers.append(event_handler)
        empty_monitor.metrics = NetworkMetrics(
            latency=150.0,
            jitter=25.0,
            packet_loss=10.0,
            throughput=30.0
        )
        
        # Should not raise an error, just log a warning
        await empty_monitor._detect_anomalies()
        
        # No events should be triggered due to missing config
        assert len(events) == 0
    
    @pytest.mark.asyncio
    async def test_partial_config_with_defaults(self):
        """Test that monitor uses defaults for missing threshold values."""
        partial_config = {
            'starlink': {
                'performance_thresholds': {
                    'max_latency': 100.0
                    # Other thresholds missing, should use defaults
                }
            }
        }
        
        partial_monitor = StarlinkMonitor(partial_config)
        events = []
        
        async def event_handler(event):
            events.append(event)
        
        partial_monitor.event_handlers.append(event_handler)
        partial_monitor.metrics = NetworkMetrics(
            latency=50.0,  # Below threshold
            jitter=25.0,   # Above default (20.0)
            packet_loss=1.0,
            throughput=100.0
        )
        
        await partial_monitor._detect_anomalies()
        
        # Should detect high jitter using default threshold
        assert len(events) == 1
        assert 'High jitter' in events[0]['data']['anomalies'][0]
