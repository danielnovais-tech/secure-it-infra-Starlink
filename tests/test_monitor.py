#!/usr/bin/env python3
"""
Basic test script for Starlink monitoring components.
Tests the core functionality without requiring actual API access.
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.starlink_api import StarlinkAPIClient
from src.metrics_collector import MetricsCollector
from src.config import (
    LATENCY_THRESHOLD,
    DOWNLINK_THRESHOLD,
    UPLINK_THRESHOLD,
    OBSTRUCTION_THRESHOLD
)


class TestStarlinkAPIClient(unittest.TestCase):
    """Test Starlink API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = StarlinkAPIClient()
    
    def test_initialization(self):
        """Test client initialization."""
        self.assertIsNotNone(self.client)
        self.assertIsNotNone(self.client.session)
    
    @patch('requests.Session.get')
    def test_get_status_success(self, mock_get):
        """Test successful status retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'state': 'CONNECTED',
            'uptime': 3600,
            'popPingLatencyMs': 45.2,
            'downlinkThroughputBps': 150_000_000,
            'uplinkThroughputBps': 25_000_000
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        status = self.client.get_status()
        
        self.assertIsNotNone(status)
        self.assertEqual(status['state'], 'CONNECTED')
        self.assertEqual(status['latency_ms'], 45.2)
    
    @patch('requests.Session.get')
    def test_get_status_timeout(self, mock_get):
        """Test API timeout handling."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        status = self.client.get_status()
        
        self.assertIsNone(status)
    
    def test_parse_status(self):
        """Test status parsing."""
        raw_data = {
            'state': 'CONNECTED',
            'uptime': 7200,
            'popPingLatencyMs': 50.0,
            'downlinkThroughputBps': 100_000_000,
            'uplinkThroughputBps': 20_000_000,
            'obstructionStats': {
                'fractionObstructed': 0.02,
                'avgProlongedObstructionDurationS': 5
            }
        }
        
        parsed = self.client._parse_status(raw_data)
        
        self.assertEqual(parsed['state'], 'CONNECTED')
        self.assertEqual(parsed['latency_ms'], 50.0)
        self.assertEqual(parsed['downlink_mbps'], 100.0)
        self.assertEqual(parsed['uplink_mbps'], 20.0)
        self.assertEqual(parsed['obstruction_percent'], 2.0)


class TestMetricsCollector(unittest.TestCase):
    """Test metrics collector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = MetricsCollector()
    
    def test_initialization(self):
        """Test collector initialization."""
        self.assertIsNotNone(self.collector)
        self.assertIsNone(self.collector.current_metrics)
        self.assertEqual(len(self.collector.events), 0)
    
    def test_update_metrics(self):
        """Test metrics update."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'state': 'CONNECTED',
            'latency_ms': 45.0,
            'downlink_mbps': 150.0,
            'uplink_mbps': 25.0,
            'obstruction_percent': 0.5
        }
        
        self.collector.update_metrics(metrics)
        
        self.assertEqual(self.collector.current_metrics, metrics)
        self.assertEqual(len(self.collector.metrics_history), 1)
    
    def test_high_latency_detection(self):
        """Test high latency event detection."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'state': 'CONNECTED',
            'latency_ms': LATENCY_THRESHOLD + 10,  # Above threshold
            'downlink_mbps': 150.0,
            'uplink_mbps': 25.0,
            'obstruction_percent': 0.5
        }
        
        self.collector.update_metrics(metrics)
        
        # Should have detected high latency event
        events = self.collector.get_recent_events()
        high_latency_events = [e for e in events if e['type'] == 'HIGH_LATENCY']
        self.assertGreater(len(high_latency_events), 0)
    
    def test_low_throughput_detection(self):
        """Test low throughput event detection."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'state': 'CONNECTED',
            'latency_ms': 45.0,
            'downlink_mbps': DOWNLINK_THRESHOLD - 10,  # Below threshold
            'uplink_mbps': UPLINK_THRESHOLD - 2,  # Below threshold
            'obstruction_percent': 0.5
        }
        
        self.collector.update_metrics(metrics)
        
        events = self.collector.get_recent_events()
        downlink_events = [e for e in events if e['type'] == 'LOW_DOWNLINK']
        uplink_events = [e for e in events if e['type'] == 'LOW_UPLINK']
        
        self.assertGreater(len(downlink_events), 0)
        self.assertGreater(len(uplink_events), 0)
    
    def test_obstruction_detection(self):
        """Test obstruction event detection."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'state': 'CONNECTED',
            'latency_ms': 45.0,
            'downlink_mbps': 150.0,
            'uplink_mbps': 25.0,
            'obstruction_percent': OBSTRUCTION_THRESHOLD + 5  # Above threshold
        }
        
        self.collector.update_metrics(metrics)
        
        events = self.collector.get_recent_events()
        obstruction_events = [e for e in events if e['type'] == 'OBSTRUCTION_DETECTED']
        self.assertGreater(len(obstruction_events), 0)
    
    def test_state_change_detection(self):
        """Test state change event detection."""
        # First update
        metrics1 = {
            'timestamp': datetime.utcnow().isoformat(),
            'state': 'SEARCHING',
            'latency_ms': 0,
            'downlink_mbps': 0,
            'uplink_mbps': 0,
            'obstruction_percent': 0
        }
        self.collector.update_metrics(metrics1)
        
        # Second update with different state
        metrics2 = {
            'timestamp': datetime.utcnow().isoformat(),
            'state': 'CONNECTED',
            'latency_ms': 45.0,
            'downlink_mbps': 150.0,
            'uplink_mbps': 25.0,
            'obstruction_percent': 0.5
        }
        self.collector.update_metrics(metrics2)
        
        events = self.collector.get_recent_events()
        state_change_events = [e for e in events if e['type'] == 'STATE_CHANGE']
        self.assertGreater(len(state_change_events), 0)
    
    def test_get_metrics_summary(self):
        """Test metrics summary generation."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'state': 'CONNECTED',
            'latency_ms': 45.0,
            'downlink_mbps': 150.0,
            'uplink_mbps': 25.0,
            'obstruction_percent': 0.5
        }
        
        self.collector.update_metrics(metrics)
        summary = self.collector.get_metrics_summary()
        
        self.assertIn('current_metrics', summary)
        self.assertIn('recent_events', summary)
        self.assertIn('status', summary)
        self.assertEqual(summary['current_metrics'], metrics)


if __name__ == '__main__':
    print("Running Starlink Monitor Tests...")
    print("=" * 60)
    unittest.main(verbosity=2)
