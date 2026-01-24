#!/usr/bin/env python3
"""
Unit tests for the Network Monitoring System
"""

import unittest
import tempfile
import os
import yaml
from network_monitor import NetworkMonitor


class TestNetworkMonitor(unittest.TestCase):
    """Test cases for NetworkMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.test_config = {
            'monitoring': {
                'targets': [
                    {
                        'host': '8.8.8.8',
                        'monitor_latency': True,
                        'monitor_jitter': True,
                        'monitor_packet_loss': True,
                        'ping_count': 4,
                        'jitter_count': 10,
                        'packet_loss_count': 20
                    },
                    {
                        'host': '1.1.1.1',
                        'monitor_latency': True,
                        'monitor_jitter': False,
                        'monitor_packet_loss': True,
                        'scan_ports': True,
                        'ports_to_scan': [80, 443],
                        'ping_count': 4,
                        'packet_loss_count': 20
                    }
                ],
                'network': {
                    'subnet': '192.168.1.0/24',
                    'detect_devices': True,
                    'check_unauthorized': True,
                    'authorized_devices': ['192.168.1.1', '192.168.1.10']
                }
            }
        }
        
        # Write config to temporary file
        self.config_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False
        )
        yaml.dump(self.test_config, self.config_file)
        self.config_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_file.name):
            os.unlink(self.config_file.name)
    
    def test_config_loading(self):
        """Test YAML configuration loading."""
        monitor = NetworkMonitor(self.config_file.name)
        self.assertIsNotNone(monitor.config)
        self.assertIn('monitoring', monitor.config)
        self.assertIn('targets', monitor.config['monitoring'])
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test missing required keys
        invalid_config = {'invalid': 'config'}
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False
        )
        yaml.dump(invalid_config, temp_file)
        temp_file.close()
        
        try:
            with self.assertRaises(ValueError):
                NetworkMonitor(temp_file.name)
        finally:
            os.unlink(temp_file.name)
    
    def test_config_file_not_found(self):
        """Test handling of missing config file."""
        with self.assertRaises(FileNotFoundError):
            NetworkMonitor('/nonexistent/config.yaml')
    
    def test_measure_latency(self):
        """Test latency measurement."""
        monitor = NetworkMonitor(self.config_file.name)
        result = monitor.measure_latency('8.8.8.8', count=2)
        
        self.assertIn('host', result)
        self.assertEqual(result['host'], '8.8.8.8')
        self.assertIn('timestamp', result)
        
        # Result should have either latency data or an error
        if 'error' not in result:
            self.assertIn('min', result)
            self.assertIn('max', result)
            self.assertIn('avg', result)
            self.assertGreater(result['min'], 0)
            self.assertGreaterEqual(result['max'], result['min'])
    
    def test_measure_jitter(self):
        """Test jitter measurement."""
        monitor = NetworkMonitor(self.config_file.name)
        result = monitor.measure_jitter('8.8.8.8', count=5)
        
        self.assertIn('host', result)
        self.assertEqual(result['host'], '8.8.8.8')
        self.assertIn('timestamp', result)
        
        # Result should have either jitter data or an error
        if 'error' not in result:
            self.assertIn('jitter_avg', result)
            self.assertIn('jitter_max', result)
            self.assertIn('jitter_min', result)
    
    def test_measure_packet_loss(self):
        """Test packet loss measurement."""
        monitor = NetworkMonitor(self.config_file.name)
        result = monitor.measure_packet_loss('8.8.8.8', count=5)
        
        self.assertIn('host', result)
        self.assertEqual(result['host'], '8.8.8.8')
        self.assertIn('timestamp', result)
        
        # Result should have either packet loss data or an error
        if 'error' not in result:
            self.assertIn('packets_sent', result)
            self.assertIn('packet_loss_percent', result)
            self.assertGreaterEqual(result['packet_loss_percent'], 0)
            self.assertLessEqual(result['packet_loss_percent'], 100)
    
    def test_measure_throughput(self):
        """Test throughput measurement."""
        monitor = NetworkMonitor(self.config_file.name)
        # Test with a known reachable host
        result = monitor.measure_throughput('8.8.8.8', port=53, duration=1)
        
        self.assertIn('host', result)
        self.assertEqual(result['host'], '8.8.8.8')
        self.assertIn('port', result)
        self.assertIn('timestamp', result)
        
        # Result should have either throughput data or an error
        # (likely error since DNS port won't accept HTTP requests)
        self.assertTrue('error' in result or 'throughput_mbps' in result)
    
    def test_scan_open_ports(self):
        """Test port scanning."""
        monitor = NetworkMonitor(self.config_file.name)
        # Scan some common ports on localhost
        result = monitor.scan_open_ports('127.0.0.1', [22, 80, 443], timeout=1)
        
        self.assertIn('host', result)
        self.assertEqual(result['host'], '127.0.0.1')
        self.assertIn('open_ports', result)
        self.assertIn('closed_ports', result)
        self.assertIn('total_scanned', result)
        self.assertEqual(result['total_scanned'], 3)
        
        # Verify open + closed = total
        total = len(result['open_ports']) + len(result['closed_ports'])
        self.assertEqual(total, result['total_scanned'])
    
    def test_detect_device_connections(self):
        """Test device connection detection."""
        monitor = NetworkMonitor(self.config_file.name)
        # Use a small network range for testing
        result = monitor.detect_device_connections('127.0.0.0/30')
        
        self.assertIn('network', result)
        self.assertIn('timestamp', result)
        
        # Result should have either device data or an error
        if 'error' not in result:
            self.assertIn('active_devices', result)
            self.assertIn('device_count', result)
            self.assertIsInstance(result['active_devices'], list)
    
    def test_check_unauthorized_devices(self):
        """Test unauthorized device detection."""
        monitor = NetworkMonitor(self.config_file.name)
        # Use a small network range for testing
        authorized = ['127.0.0.1']
        result = monitor.check_unauthorized_devices('127.0.0.0/30', authorized)
        
        self.assertIn('network', result)
        self.assertIn('timestamp', result)
        
        # Result should have either unauthorized device data or an error
        if 'error' not in result:
            self.assertIn('unauthorized_devices', result)
            self.assertIn('unauthorized_count', result)
            self.assertIn('total_active', result)
            self.assertIsInstance(result['unauthorized_devices'], list)
    
    def test_run_monitoring(self):
        """Test full monitoring run."""
        monitor = NetworkMonitor(self.config_file.name)
        results = monitor.run_monitoring()
        
        # Check for required top-level keys
        self.assertIn('monitoring_start', results)
        self.assertIn('monitoring_end', results)
        self.assertIn('latency', results)
        self.assertIn('jitter', results)
        self.assertIn('packet_loss', results)
        self.assertIn('throughput', results)
        self.assertIn('open_ports', results)
        self.assertIn('device_connections', results)
        self.assertIn('unauthorized_devices', results)
        
        # Verify lists are populated based on config
        self.assertIsInstance(results['latency'], list)
        self.assertIsInstance(results['jitter'], list)
        self.assertIsInstance(results['packet_loss'], list)
    
    def test_generate_report(self):
        """Test report generation."""
        monitor = NetworkMonitor(self.config_file.name)
        
        # Create sample results
        sample_results = {
            'monitoring_start': '2026-01-06T00:00:00',
            'monitoring_end': '2026-01-06T00:05:00',
            'latency': [
                {
                    'host': '8.8.8.8',
                    'min': 10.5,
                    'max': 15.2,
                    'avg': 12.8,
                    'count': 4,
                    'timestamp': '2026-01-06T00:01:00'
                }
            ],
            'jitter': [],
            'packet_loss': [],
            'throughput': [],
            'open_ports': [],
            'device_connections': [],
            'unauthorized_devices': []
        }
        
        report = monitor.generate_report(sample_results)
        
        # Verify report contains expected sections
        self.assertIn('NETWORK MONITORING REPORT', report)
        self.assertIn('LATENCY MONITORING', report)
        self.assertIn('8.8.8.8', report)
        self.assertIn('Min: 10.50 ms', report)
        self.assertIn('Max: 15.20 ms', report)
        self.assertIn('Avg: 12.80 ms', report)
    
    def test_generate_report_to_file(self):
        """Test report generation to file."""
        monitor = NetworkMonitor(self.config_file.name)
        
        sample_results = {
            'monitoring_start': '2026-01-06T00:00:00',
            'monitoring_end': '2026-01-06T00:05:00',
            'latency': [],
            'jitter': [],
            'packet_loss': [],
            'throughput': [],
            'open_ports': [],
            'device_connections': [],
            'unauthorized_devices': []
        }
        
        # Generate report to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_file = f.name
        
        try:
            monitor.generate_report(sample_results, output_file)
            
            # Verify file was created and contains content
            self.assertTrue(os.path.exists(output_file))
            with open(output_file, 'r') as f:
                content = f.read()
                self.assertIn('NETWORK MONITORING REPORT', content)
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_report_with_unauthorized_devices(self):
        """Test report generation with unauthorized devices."""
        monitor = NetworkMonitor(self.config_file.name)
        
        sample_results = {
            'monitoring_start': '2026-01-06T00:00:00',
            'monitoring_end': '2026-01-06T00:05:00',
            'latency': [],
            'jitter': [],
            'packet_loss': [],
            'throughput': [],
            'open_ports': [],
            'device_connections': [],
            'unauthorized_devices': [
                {
                    'network': '192.168.1.0/24',
                    'unauthorized_devices': ['192.168.1.50', '192.168.1.51'],
                    'unauthorized_count': 2,
                    'total_active': 5,
                    'timestamp': '2026-01-06T00:03:00'
                }
            ]
        }
        
        report = monitor.generate_report(sample_results)
        
        # Verify unauthorized devices section
        self.assertIn('UNAUTHORIZED DEVICES DETECTION', report)
        self.assertIn('WARNING', report)
        self.assertIn('192.168.1.50', report)
        self.assertIn('192.168.1.51', report)
    
    def test_report_with_open_ports(self):
        """Test report generation with open ports."""
        monitor = NetworkMonitor(self.config_file.name)
        
        sample_results = {
            'monitoring_start': '2026-01-06T00:00:00',
            'monitoring_end': '2026-01-06T00:05:00',
            'latency': [],
            'jitter': [],
            'packet_loss': [],
            'throughput': [],
            'open_ports': [
                {
                    'host': '192.168.1.1',
                    'open_ports': [22, 80, 443],
                    'closed_ports': [23, 3389],
                    'total_scanned': 5,
                    'timestamp': '2026-01-06T00:02:00'
                }
            ],
            'device_connections': [],
            'unauthorized_devices': []
        }
        
        report = monitor.generate_report(sample_results)
        
        # Verify open ports section
        self.assertIn('OPEN PORTS SCAN', report)
        self.assertIn('192.168.1.1', report)
        self.assertIn('[22, 80, 443]', report)


if __name__ == '__main__':
    unittest.main()
