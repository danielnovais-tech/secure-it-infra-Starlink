"""
Unit tests for Starlink Security Monitoring System
"""

import unittest
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
        time.sleep(0.01)  # Small delay to ensure timestamp changes
        
        self.monitor.update_metrics(signal_quality=95.0)
        
        self.assertGreater(self.monitor.metrics.last_updated, initial_timestamp)
    
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
