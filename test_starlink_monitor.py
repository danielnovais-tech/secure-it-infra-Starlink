"""
Tests for Starlink Network Monitoring System
"""
import pytest
import json
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
