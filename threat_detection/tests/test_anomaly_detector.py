"""
Tests for Anomaly Detector
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from anomaly_detector import AnomalyDetector


def test_failed_login_detection():
    """Test failed login anomaly detection"""
    config = {
        'thresholds': {
            'failed_login_threshold': 3,
            'failed_login_window_minutes': 10
        }
    }
    
    detector = AnomalyDetector(config)
    
    # First two attempts should not trigger
    event1 = {'type': 'failed_login', 'ip_address': '192.168.1.100'}
    anomalies1 = detector.analyze(event1)
    assert len(anomalies1) == 0
    
    event2 = {'type': 'failed_login', 'ip_address': '192.168.1.100'}
    anomalies2 = detector.analyze(event2)
    assert len(anomalies2) == 0
    
    # Third attempt should trigger anomaly
    event3 = {'type': 'failed_login', 'ip_address': '192.168.1.100'}
    anomalies3 = detector.analyze(event3)
    assert len(anomalies3) == 1
    assert anomalies3[0]['type'] == 'failed_login_anomaly'
    assert anomalies3[0]['ip_address'] == '192.168.1.100'
    
    print("✓ Failed login detection test passed")


def test_connection_rate_detection():
    """Test connection rate anomaly detection"""
    config = {
        'thresholds': {
            'connection_rate_threshold': 3,
            'connection_rate_window_seconds': 60
        }
    }
    
    detector = AnomalyDetector(config)
    
    # Simulate multiple connections
    for i in range(2):
        event = {'type': 'connection', 'ip_address': '10.0.0.50'}
        anomalies = detector.analyze(event)
        assert len(anomalies) == 0
    
    # Third connection should trigger
    event = {'type': 'connection', 'ip_address': '10.0.0.50'}
    anomalies = detector.analyze(event)
    assert len(anomalies) == 1
    assert anomalies[0]['type'] == 'connection_rate_anomaly'
    
    print("✓ Connection rate detection test passed")


def test_bandwidth_usage_detection():
    """Test bandwidth usage anomaly detection"""
    config = {
        'thresholds': {
            'bandwidth_threshold_mb': 1,  # 1 MB threshold
            'bandwidth_window_minutes': 5
        }
    }
    
    detector = AnomalyDetector(config)
    
    # Transfer 1.5 MB (should trigger)
    event = {
        'type': 'bandwidth',
        'ip_address': '172.16.0.10',
        'bytes': 1.5 * 1024 * 1024  # 1.5 MB in bytes
    }
    anomalies = detector.analyze(event)
    assert len(anomalies) == 1
    assert anomalies[0]['type'] == 'bandwidth_anomaly'
    
    print("✓ Bandwidth usage detection test passed")


def test_port_scan_detection():
    """Test port scan anomaly detection"""
    config = {
        'thresholds': {
            'port_scan_threshold': 3,
            'port_scan_window_seconds': 30
        }
    }
    
    detector = AnomalyDetector(config)
    
    # Access 3 different ports
    ports = [22, 80, 443]
    for i, port in enumerate(ports):
        event = {
            'type': 'port_access',
            'ip_address': '203.0.113.50',
            'port': port
        }
        anomalies = detector.analyze(event)
        
        if i < 2:
            assert len(anomalies) == 0
        else:
            # Third unique port should trigger
            assert len(anomalies) == 1
            assert anomalies[0]['type'] == 'port_scan_anomaly'
    
    print("✓ Port scan detection test passed")


if __name__ == '__main__':
    test_failed_login_detection()
    test_connection_rate_detection()
    test_bandwidth_usage_detection()
    test_port_scan_detection()
    print("\n✓ All anomaly detector tests passed!")
