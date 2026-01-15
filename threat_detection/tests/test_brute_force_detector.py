"""
Tests for Brute-force Detector
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from brute_force_detector import BruteForceDetector


def test_ssh_bruteforce_detection():
    """Test SSH brute-force pattern detection"""
    config = {
        'patterns': [
            {
                'name': 'SSH Brute-force',
                'pattern': r'Failed password for .* from (\d+\.\d+\.\d+\.\d+)',
                'threshold': 3,
                'window_minutes': 10,
                'action': 'block'
            }
        ]
    }
    
    detector = BruteForceDetector(config)
    
    # Simulate log lines
    log_lines = [
        "Jan 6 10:00:01 server sshd[1234]: Failed password for root from 192.168.1.100 port 22",
        "Jan 6 10:00:05 server sshd[1235]: Failed password for admin from 192.168.1.100 port 22",
        "Jan 6 10:00:10 server sshd[1236]: Failed password for user from 192.168.1.100 port 22"
    ]
    
    detections = []
    for line in log_lines:
        result = detector.analyze_log_line(line)
        detections.extend(result)
    
    # Should detect brute-force on third attempt
    assert len(detections) == 1
    assert detections[0]['pattern_name'] == 'SSH Brute-force'
    assert detections[0]['ip_address'] == '192.168.1.100'
    assert detections[0]['attempt_count'] == 3
    assert detections[0]['action'] == 'block'
    
    print("✓ SSH brute-force detection test passed")


def test_http_bruteforce_detection():
    """Test HTTP authentication brute-force detection"""
    config = {
        'patterns': [
            {
                'name': 'HTTP Auth Brute-force',
                'pattern': r'(\d+\.\d+\.\d+\.\d+).*POST.*/login.*401',
                'threshold': 2,
                'window_minutes': 5,
                'action': 'alert'
            }
        ]
    }
    
    detector = BruteForceDetector(config)
    
    # Simulate HTTP log lines
    log_lines = [
        '192.168.1.50 - - [06/Jan/2026:10:00:01 +0000] "POST /login HTTP/1.1" 401 512',
        '192.168.1.50 - - [06/Jan/2026:10:00:05 +0000] "POST /login HTTP/1.1" 401 512'
    ]
    
    detections = []
    for line in log_lines:
        result = detector.analyze_log_line(line)
        detections.extend(result)
    
    # Should detect on second attempt
    assert len(detections) == 1
    assert detections[0]['pattern_name'] == 'HTTP Auth Brute-force'
    assert detections[0]['ip_address'] == '192.168.1.50'
    
    print("✓ HTTP brute-force detection test passed")


def test_log_file_analysis():
    """Test analyzing complete log file"""
    config = {
        'patterns': [
            {
                'name': 'Test Pattern',
                'pattern': r'FAILED.*from (\d+\.\d+\.\d+\.\d+)',
                'threshold': 2,
                'window_minutes': 10,
                'action': 'block'
            }
        ]
    }
    
    detector = BruteForceDetector(config)
    
    # Create temporary log file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write("FAILED login attempt from 10.0.0.1\n")
        f.write("Normal log entry\n")
        f.write("FAILED login attempt from 10.0.0.1\n")
        temp_log = f.name
    
    try:
        detections = detector.analyze_log_file(temp_log)
        
        # Should detect brute-force
        assert len(detections) == 1
        assert detections[0]['ip_address'] == '10.0.0.1'
        
        print("✓ Log file analysis test passed")
    finally:
        os.unlink(temp_log)


def test_blocked_ips():
    """Test getting blocked IPs"""
    config = {
        'patterns': [
            {
                'name': 'Block Pattern',
                'pattern': r'ATTACK from (\d+\.\d+\.\d+\.\d+)',
                'threshold': 2,
                'window_minutes': 10,
                'action': 'block'
            },
            {
                'name': 'Alert Pattern',
                'pattern': r'WARNING from (\d+\.\d+\.\d+\.\d+)',
                'threshold': 2,
                'window_minutes': 10,
                'action': 'alert'
            }
        ]
    }
    
    detector = BruteForceDetector(config)
    
    # Trigger block pattern
    for i in range(2):
        detector.analyze_log_line("ATTACK from 192.168.1.1")
    
    # Trigger alert pattern (should not be blocked)
    for i in range(2):
        detector.analyze_log_line("WARNING from 192.168.1.2")
    
    blocked = detector.get_blocked_ips()
    
    # Only IPs from 'block' action should be in list
    assert '192.168.1.1' in blocked
    assert '192.168.1.2' not in blocked
    
    print("✓ Blocked IPs test passed")


if __name__ == '__main__':
    test_ssh_bruteforce_detection()
    test_http_bruteforce_detection()
    test_log_file_analysis()
    test_blocked_ips()
    print("\n✓ All brute-force detector tests passed!")
