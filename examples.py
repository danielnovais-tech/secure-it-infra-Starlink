#!/usr/bin/env python3
"""
Example usage of the Threat Detection System
Demonstrates various features and capabilities
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from threat_detection.threat_detection import ThreatDetectionSystem


def example_anomaly_detection():
    """Demonstrate anomaly detection"""
    print("=" * 60)
    print("EXAMPLE 1: Anomaly Detection")
    print("=" * 60)
    
    system = ThreatDetectionSystem()
    
    # Simulate failed login attempts
    print("\nSimulating 5 failed login attempts from same IP...")
    for i in range(5):
        event = {
            'type': 'failed_login',
            'ip_address': '192.168.1.100',
            'timestamp': '2026-01-06T12:00:00'
        }
        threats = system.analyze_event(event)
        
        if threats:
            print(f"  Attempt {i+1}: THREAT DETECTED!")
            for threat in threats:
                print(f"    - {threat['description']}")
        else:
            print(f"  Attempt {i+1}: Normal activity")
    
    print()


def example_port_scan_detection():
    """Demonstrate port scan detection"""
    print("=" * 60)
    print("EXAMPLE 2: Port Scan Detection")
    print("=" * 60)
    
    system = ThreatDetectionSystem()
    
    # Simulate port scanning
    print("\nSimulating port scan (accessing 15 different ports)...")
    ports = [22, 80, 443, 21, 25, 53, 110, 143, 3306, 5432, 8080, 8443, 3389, 5900, 6379]
    
    for i, port in enumerate(ports):
        event = {
            'type': 'port_access',
            'ip_address': '203.0.113.50',
            'port': port
        }
        threats = system.analyze_event(event)
        
        if threats:
            print(f"  Port {port}: PORT SCAN DETECTED!")
            for threat in threats:
                print(f"    - {threat['description']}")
            break
        else:
            print(f"  Port {port}: Normal activity")
    
    print()


def example_brute_force_detection():
    """Demonstrate brute-force attack detection"""
    print("=" * 60)
    print("EXAMPLE 3: Brute-force Attack Detection")
    print("=" * 60)
    
    import tempfile
    
    # Create sample log file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write("Jan  6 10:00:01 server sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2\n")
        f.write("Jan  6 10:00:05 server sshd[1235]: Accepted password for user from 192.168.1.101 port 22 ssh2\n")
        f.write("Jan  6 10:00:10 server sshd[1236]: Failed password for admin from 192.168.1.100 port 22 ssh2\n")
        f.write("Jan  6 10:00:15 server sshd[1237]: Failed password for user from 192.168.1.100 port 22 ssh2\n")
        f.write("Jan  6 10:00:20 server sshd[1238]: Failed password for test from 192.168.1.100 port 22 ssh2\n")
        f.write("Jan  6 10:00:25 server sshd[1239]: Failed password for ubuntu from 192.168.1.100 port 22 ssh2\n")
        temp_log = f.name
    
    try:
        system = ThreatDetectionSystem()
        
        print(f"\nAnalyzing log file: {temp_log}")
        detections = system.analyze_log_file(temp_log)
        
        if detections:
            print(f"\nDetected {len(detections)} brute-force attack(s):")
            for detection in detections:
                print(f"  - Pattern: {detection['pattern_name']}")
                print(f"    IP Address: {detection['ip_address']}")
                print(f"    Attempts: {detection['attempt_count']}")
                print(f"    Action: {detection['action']}")
                print()
        else:
            print("\nNo brute-force attacks detected")
    finally:
        os.unlink(temp_log)


def example_threat_intelligence():
    """Demonstrate threat intelligence checking"""
    print("=" * 60)
    print("EXAMPLE 4: Threat Intelligence Integration")
    print("=" * 60)
    
    system = ThreatDetectionSystem()
    
    # Note: This would normally download from actual feeds
    # For demo purposes, we'll manually add some IPs
    if system.threat_intelligence:
        print("\nManually adding known threat IPs for demonstration...")
        system.threat_intelligence.threat_ips.add('198.51.100.1')
        system.threat_intelligence.threat_ips.add('198.51.100.2')
        print("  Added: 198.51.100.1, 198.51.100.2")
        
        print("\nChecking IP addresses against threat intelligence...")
        
        # Check a threat IP
        event1 = {
            'type': 'connection',
            'ip_address': '198.51.100.1',
        }
        threats1 = system.analyze_event(event1)
        
        if threats1:
            print(f"  IP 198.51.100.1: KNOWN THREAT!")
            for threat in threats1:
                print(f"    - {threat['description']}")
        
        # Check a clean IP
        event2 = {
            'type': 'connection',
            'ip_address': '8.8.8.8',
        }
        threats2 = system.analyze_event(event2)
        
        if not threats2:
            print(f"  IP 8.8.8.8: Clean (not in threat feeds)")
    
    print()


def example_blocked_ips():
    """Demonstrate getting blocked IPs"""
    print("=" * 60)
    print("EXAMPLE 5: Getting Blocked IP List")
    print("=" * 60)
    
    system = ThreatDetectionSystem()
    
    # Trigger some brute-force detections
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        for i in range(6):
            f.write(f"Failed password for user from 192.168.1.200 port 22 ssh2\n")
        temp_log = f.name
    
    try:
        system.analyze_log_file(temp_log)
        
        blocked_ips = system.get_blocked_ips()
        
        print(f"\nTotal IPs to block: {len(blocked_ips)}")
        print("\nBlocked IP addresses:")
        for ip in blocked_ips[:10]:  # Show first 10
            print(f"  - {ip}")
        
        if len(blocked_ips) > 10:
            print(f"  ... and {len(blocked_ips) - 10} more")
    finally:
        os.unlink(temp_log)
    
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  THREAT DETECTION SYSTEM - USAGE EXAMPLES".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        example_anomaly_detection()
        example_port_scan_detection()
        example_brute_force_detection()
        example_threat_intelligence()
        example_blocked_ips()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
