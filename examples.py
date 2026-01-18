#!/usr/bin/env python3
"""
Example script demonstrating VPN Manager API usage
Shows how to integrate VPN management into your own applications
"""

from vpn_manager.vpn_manager import VPNManager as CoreVPNManager
import time
import sys
from typing import Any


def example_basic_usage():
    # Basic VPN manager usage example
    print("=== Basic VPN Manager Usage ===\n")
    
    # Initialize the manager
    manager = CoreVPNManager('config/vpn_config.yaml')
    
    # Check current status
    print("1. Checking VPN status...")
    status = manager.get_vpn_status()
    print(f"   Connected: {status['connected']}")
    print(f"   Healthy: {status['healthy']}")
    print(f"   Connection: {status['connection_name']}\n")
    
    # Get configuration info
    print("2. Configuration details:")
    print(f"   Status retrieved successfully\n")


def example_connection_management():
    # Example of managing VPN connections
    print("=== VPN Connection Management ===\n")
    
    # NOTE: CoreVPNManager may be missing type information in this repo, so we
    # treat it as `Any` to avoid false-positive attribute errors from type checkers.
    manager: Any = CoreVPNManager('config/vpn_config.yaml')
    
    # Connect to VPN
    print("1. Attempting to connect to VPN...")
    if manager.connect():
        print("   ✓ Successfully connected to VPN\n")
        
        # Wait and check status
        time.sleep(2)
        status = manager.get_vpn_status()
        print(f"   Status after connection: {status['connected']}\n")
        
        # Disconnect
        print("2. Disconnecting from VPN...")
        if manager.disconnect():
            print("   ✓ Successfully disconnected\n")
    else:
        print("   ✗ Failed to connect (may need root permissions)\n")


def example_monitoring_loop():
    # Example of a custom monitoring loop
    print("=== Custom Monitoring Loop ===\n")
    print("Monitoring VPN for 30 seconds...\n")
    
    # See note in `example_connection_management` about missing type information.
    manager: Any = CoreVPNManager('config/vpn_config.yaml')
    
    # Custom monitoring loop
    iterations = 3
    for i in range(iterations):
        status = manager.get_vpn_status()
        
        print(f"Check {i+1}/{iterations}:")
        print(f"  Time: {status['timestamp']}")
        print(f"  Connected: {status['connected']}")
        print(f"  Healthy: {status['healthy']}")
        
        if not status['connected']:
            print("  ⚠ VPN is disconnected!")
            print("  → Attempting reconnection...")
            if manager.connect():
                print("  ✓ Reconnected successfully")
            else:
                print("  ✗ Reconnection failed")
        elif not status['healthy']:
            print("  ⚠ VPN connection is unhealthy!")
        else:
            print("  ✓ VPN is healthy")
        
        print()
        
        if i < iterations - 1:
            time.sleep(10)


def example_health_check():
    # Example of health check functionality
    print("=== VPN Health Check ===\n")
    
    manager = CoreVPNManager('config/vpn_config.yaml')
    
    # Get status with health check
    status = manager.get_vpn_status()
    
    print(f"Connection Status: {status['connected']}")
    print(f"Health Status: {status['healthy']}")
    
    if status['connected'] and not status['healthy']:
        print("\n⚠ Warning: VPN is connected but health check failed!")
        print("This may indicate:")
        print("  - DNS resolution issues")
        print("  - Firewall blocking traffic")
        print("  - Routing problems")
        print("  - Test hosts unreachable")
    elif not status['connected']:
        print("\n⚠ VPN is not connected")
    else:
        print("\n✓ VPN is connected and healthy")




    """Example usage of the Threat Detection System
    Demonstrates various features and capabilities
    """

import sys
import os

# Add threat_detection directory to path
sys.path.insert(0, os.path.dirname(__file__))

from threat_detection.threat_detection import ThreatDetectionSystem


def example_anomaly_detection():
    # Demonstrate anomaly detection
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
    # Demonstrate port scan detection
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
    # Demonstrate brute-force attack detection
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
    # Demonstrate threat intelligence checking
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
    # Demonstrate getting blocked IPs
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
    # Run all examples
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

# Example usage scenarios for Security Modules
# Demonstrates practical implementations of the security framework

import logging
from security_modules import (
    NetworkMonitor,
    ThreatDetector,
    PolicyEnforcer,
    IncidentResponder,
    VPNManager as SecurityVPNManager,
    BackupManager
)
from security_modules.policy_enforcer import SecurityLevel
from security_modules.threat_detector import ThreatLevel
from security_modules.incident_responder import IncidentSeverity
from security_modules.vpn_manager import VPNProtocol
from security_modules.backup_manager import BackupType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_security_incident_workflow():
    # Example: Complete security incident response workflow
    # Scenario: Malware detected on network device
    logger.info("\n=== Security Incident Workflow Example ===\n")
    
    # Initialize modules
    network_monitor = NetworkMonitor("10.0.0.0/24")
    threat_detector = ThreatDetector()
    policy_enforcer = PolicyEnforcer()
    incident_responder = IncidentResponder()
    
    # Step 1: Network monitoring detects anomaly
    logger.info("Step 1: Network monitoring...")
    devices = network_monitor.discover_devices()
    anomalies = network_monitor.detect_anomalies()
    
    # Step 2: Threat detector analyzes suspicious activity
    logger.info("Step 2: Analyzing threat...")
    threat_id = threat_detector.report_threat(
        "malware_detected",
        {
            "device": "10.0.0.55",
            "signature": "Trojan.Generic.123456",
            "affected_files": ["/tmp/malicious.exe"]
        },
        ThreatLevel.CRITICAL
    )
    
    # Step 3: Escalate security level
    logger.info("Step 3: Escalating security level...")
    policy_enforcer.set_security_level(SecurityLevel.HIGH)
    
    # Step 4: Create and auto-respond to incident
    logger.info("Step 4: Creating incident and initiating response...")
    incident_id = incident_responder.create_incident(
        incident_type="malware",
        severity=IncidentSeverity.CRITICAL,
        description=f"Malware detected: {threat_id}",
        affected_systems=["10.0.0.55"]
    )
    
    # Step 5: Verify response actions
    logger.info("Step 5: Verifying response actions...")
    incident_summary = incident_responder.get_incident_summary()
    logger.info(f"Incident Summary: {incident_summary}")
    
    # Step 6: Resolution
    logger.info("Step 6: Resolving incident...")
    incident_responder.resolve_incident(
        incident_id,
        "Malware isolated and removed. System scanned clean. Security policies updated."
    )
    
    logger.info("\n=== Incident Workflow Completed ===\n")


def example_vpn_failover_scenario():
    # Example: VPN failover with backup management
    # Scenario: Primary VPN connection fails, automatic failover to backup
    logger.info("\n=== VPN Failover Scenario Example ===\n")
    
    # Initialize modules
    vpn_manager = SecurityVPNManager(default_protocol=VPNProtocol.WIREGUARD)
    backup_manager = BackupManager()
    incident_responder = IncidentResponder()
    
    # Step 1: Configure primary and backup VPN
    logger.info("Step 1: Configuring VPN connections...")
    primary_vpn = vpn_manager.create_vpn_config(
        "Primary VPN",
        VPNProtocol.WIREGUARD,
        "vpn-primary.starlink.com",
        51820
    )
    
    backup_vpn = vpn_manager.create_vpn_config(
        "Backup VPN",
        VPNProtocol.WIREGUARD,
        "vpn-backup.starlink.com",
        51820
    )
    
    # Step 2: Connect to primary VPN
    logger.info("Step 2: Connecting to primary VPN...")
    vpn_manager.connect(primary_vpn)
    
    # Step 3: Enable VPN failover
    logger.info("Step 3: Enabling failover...")
    vpn_manager.enable_failover(primary_vpn, backup_vpn)
    
    # Step 4: Configure service failover in backup manager
    logger.info("Step 4: Configuring service failover...")
    failover_id = backup_manager.configure_failover(
        service_name="VPN Gateway",
        primary_endpoint="vpn-primary.starlink.com",
        backup_endpoints=["vpn-backup.starlink.com", "vpn-tertiary.starlink.com"]
    )
    
    # Step 5: Simulate primary VPN failure
    logger.info("Step 5: Simulating primary VPN failure...")
    incident_id = incident_responder.create_incident(
        incident_type="vpn_failure",
        severity=IncidentSeverity.HIGH,
        description="Primary VPN connection lost",
        affected_systems=["vpn-primary.starlink.com"]
    )
    
    # Step 6: Trigger failover
    logger.info("Step 6: Triggering failover...")
    backup_manager.trigger_failover(failover_id, "Primary VPN unavailable")
    vpn_manager.disconnect(primary_vpn)
    vpn_manager.connect(backup_vpn)
    
    # Step 7: Verify failover success
    logger.info("Step 7: Verifying failover...")
    vpn_status = vpn_manager.get_vpn_statistics()
    logger.info(f"VPN Status: {vpn_status}")
    
    logger.info("\n=== VPN Failover Scenario Completed ===\n")


def example_comprehensive_backup_strategy():
    # Example: Comprehensive backup and recovery strategy
    # Scenario: Implementing multi-tier backup with redundancy
    logger.info("\n=== Comprehensive Backup Strategy Example ===\n")
    
    # Initialize backup manager
    backup_manager = BackupManager()
    
    # Step 1: Create full system backup
    logger.info("Step 1: Creating full system backup...")
    full_backup_id = backup_manager.create_backup(
        backup_name="Weekly Full Backup",
        backup_type=BackupType.FULL,
        source_paths=["/var/lib/starlink", "/etc/starlink", "/opt/starlink"],
        destination="/backups/weekly",
        encryption=True
    )
    
    # Step 2: Verify backup integrity
    logger.info("Step 2: Verifying backup...")
    backup_manager.verify_backup(full_backup_id)
    
    # Step 3: Create incremental backups
    logger.info("Step 3: Creating incremental backups...")
    for day in range(1, 4):
        incremental_id = backup_manager.create_backup(
            backup_name=f"Daily Incremental Day {day}",
            backup_type=BackupType.INCREMENTAL,
            source_paths=["/var/lib/starlink"],
            destination=f"/backups/daily/day{day}",
            encryption=True
        )
        backup_manager.verify_backup(incremental_id)
    
    # Step 4: Configure failover for critical services
    logger.info("Step 4: Configuring service failover...")
    services = [
        ("Database", "db-1.local", ["db-2.local", "db-3.local"]),
        ("API Gateway", "api-1.local", ["api-2.local", "api-3.local"]),
        ("Authentication", "auth-1.local", ["auth-2.local"])
    ]
    
    for service_name, primary, backups in services:
        backup_manager.configure_failover(
            service_name=service_name,
            primary_endpoint=primary,
            backup_endpoints=backups,
            health_check_interval=30
        )
    
    # Step 5: Check redundancy status
    logger.info("Step 5: Checking redundancy...")
    for service_name, _, _ in services:
        redundancy = backup_manager.check_redundancy(service_name, required_replicas=2)
        logger.info(f"{service_name} redundancy: {redundancy['is_redundant']}")
    
    # Step 6: Get overall backup status
    logger.info("Step 6: Getting backup status...")
    status = backup_manager.get_backup_status()
    logger.info(f"Backup Status: {status}")
    
    logger.info("\n=== Comprehensive Backup Strategy Completed ===\n")


def example_threat_hunting_workflow():
    # Example: Proactive threat hunting workflow
    # Scenario: Search for indicators of compromise across the infrastructure
    logger.info("\n=== Threat Hunting Workflow Example ===\n")
    
    # Initialize modules
    network_monitor = NetworkMonitor("172.16.0.0/16")
    threat_detector = ThreatDetector()
    policy_enforcer = PolicyEnforcer()
    
    # Step 1: Update threat intelligence
    logger.info("Step 1: Updating threat intelligence feeds...")
    threat_detector.update_threat_feeds([
        "https://otx.alienvault.com/api/v1/pulses/subscribed",
        "https://threatfeeds.example.com/iocs"
    ])
    
    # Step 2: Scan network for devices
    logger.info("Step 2: Scanning network...")
    devices = network_monitor.discover_devices()
    
    # Step 3: Check suspicious IPs
    logger.info("Step 3: Checking IP reputations...")
    suspicious_ips = ["192.168.1.100", "10.0.0.50", "172.16.0.200"]
    
    for ip in suspicious_ips:
        reputation = threat_detector.check_ip_reputation(ip)
        if reputation["is_malicious"]:
            logger.warning(f"Malicious IP detected: {ip}")
            
            # Apply policy to block
            policy_enforcer.add_custom_policy(
                f"block_{ip}",
                {"source_ip": ip, "action": "deny"}
            )
    
    # Step 4: Analyze system logs
    logger.info("Step 4: Analyzing logs for threats...")
    log_files = ["/var/log/auth.log", "/var/log/syslog", "/var/log/starlink.log"]
    
    for log_file in log_files:
        events = threat_detector.analyze_logs(log_file)
        if events:
            logger.warning(f"Security events found in {log_file}: {len(events)}")
    
    # Step 5: Get threat summary
    logger.info("Step 5: Getting threat summary...")
    summary = threat_detector.get_threat_summary()
    logger.info(f"Threat Summary: {summary}")
    
    logger.info("\n=== Threat Hunting Workflow Completed ===\n")


if __name__ == "__main__":
    logger.info("Starting Security Module Examples\n")
    
    # Run example scenarios
    example_security_incident_workflow()
    example_vpn_failover_scenario()
    example_comprehensive_backup_strategy()
    example_threat_hunting_workflow()
    
    logger.info("All examples completed successfully!")
