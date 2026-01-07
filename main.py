"""
Main application for Secure IT Infrastructure - Starlink
Integrates all security modules for comprehensive infrastructure protection.
"""

import logging
import sys
from security_modules import (
    NetworkMonitor,
    ThreatDetector,
    PolicyEnforcer,
    IncidentResponder,
    VPNManager,
    BackupManager
)
from security_modules.policy_enforcer import SecurityLevel
from security_modules.threat_detector import ThreatLevel
from security_modules.incident_responder import IncidentSeverity
from security_modules.vpn_manager import VPNProtocol
from security_modules.backup_manager import BackupType


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('security_system.log')
        ]
    )


def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Secure IT Infrastructure - Starlink")
    logger.info("Security Modules System Starting")
    logger.info("=" * 60)
    
    # Initialize all security modules
    logger.info("\nInitializing Security Modules...")
    
    # Network Monitor
    network_monitor = NetworkMonitor(network_range="10.0.0.0/24")
    logger.info("✓ Network Monitor initialized")
    
    # Threat Detector
    threat_detector = ThreatDetector()
    threat_detector.update_threat_feeds([
        "https://threat-feed-1.example.com",
        "https://threat-feed-2.example.com"
    ])
    logger.info("✓ Threat Detector initialized")
    
    # Policy Enforcer
    policy_enforcer = PolicyEnforcer(default_security_level=SecurityLevel.HIGH)
    logger.info("✓ Policy Enforcer initialized")
    
    # Incident Responder
    incident_responder = IncidentResponder()
    logger.info("✓ Incident Responder initialized")
    
    # VPN Manager
    vpn_manager = VPNManager(default_protocol=VPNProtocol.WIREGUARD)
    logger.info("✓ VPN Manager initialized")
    
    # Backup Manager
    backup_manager = BackupManager()
    logger.info("✓ Backup Manager initialized")
    
    logger.info("\nAll security modules initialized successfully!")
    
    # Demonstrate functionality
    logger.info("\n" + "=" * 60)
    logger.info("Demonstrating Security Module Capabilities")
    logger.info("=" * 60)
    
    # Network monitoring example
    logger.info("\n--- Network Monitor Demo ---")
    network_monitor.discover_devices()
    port_scan = network_monitor.scan_ports("10.0.0.100")
    network_status = network_monitor.get_network_status()
    logger.info(f"Network Status: {network_status}")
    
    # Threat detection example
    logger.info("\n--- Threat Detector Demo ---")
    threat_id = threat_detector.report_threat(
        "suspicious_activity",
        {"source_ip": "192.168.1.50", "description": "Multiple failed login attempts"},
        ThreatLevel.MEDIUM
    )
    threat_summary = threat_detector.get_threat_summary()
    logger.info(f"Threat Summary: {threat_summary}")
    
    # Policy enforcement example
    logger.info("\n--- Policy Enforcer Demo ---")
    policy_enforcer.set_security_level(SecurityLevel.HIGH)
    policy_decision = policy_enforcer.enforce_policy(
        resource="database",
        action="write",
        context={"user": "admin", "authenticated": True}
    )
    policy_status = policy_enforcer.get_policy_status()
    logger.info(f"Policy Status: {policy_status}")
    
    # Incident response example
    logger.info("\n--- Incident Responder Demo ---")
    incident_id = incident_responder.create_incident(
        incident_type="malware",
        severity=IncidentSeverity.HIGH,
        description="Malware detected on endpoint",
        affected_systems=["workstation-01"]
    )
    incident_summary = incident_responder.get_incident_summary()
    logger.info(f"Incident Summary: {incident_summary}")
    
    # VPN management example
    logger.info("\n--- VPN Manager Demo ---")
    vpn_config_id = vpn_manager.create_vpn_config(
        config_name="Starlink Primary VPN",
        protocol=VPNProtocol.WIREGUARD,
        server="vpn.starlink.example.com",
        port=51820
    )
    vpn_manager.connect(vpn_config_id)
    vpn_stats = vpn_manager.get_vpn_statistics()
    logger.info(f"VPN Statistics: {vpn_stats}")
    
    # Backup management example
    logger.info("\n--- Backup Manager Demo ---")
    backup_id = backup_manager.create_backup(
        backup_name="Daily System Backup",
        backup_type=BackupType.FULL,
        source_paths=["/var/lib/starlink", "/etc/starlink"],
        destination="/backup/starlink"
    )
    backup_manager.verify_backup(backup_id)
    
    failover_id = backup_manager.configure_failover(
        service_name="Starlink Gateway",
        primary_endpoint="gateway-1.starlink.local",
        backup_endpoints=["gateway-2.starlink.local", "gateway-3.starlink.local"]
    )
    
    backup_status = backup_manager.get_backup_status()
    logger.info(f"Backup Status: {backup_status}")
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("Security System Status Summary")
    logger.info("=" * 60)
    logger.info(f"Network Monitoring: {network_status['discovered_devices']} devices, {network_status['total_anomalies']} anomalies")
    logger.info(f"Threat Detection: {threat_summary['total_threats']} threats detected")
    logger.info(f"Policy Enforcement: Security Level {policy_status['security_level']}, {policy_status['active_policies']} policies active")
    logger.info(f"Incident Response: {incident_summary['total_incidents']} incidents, {incident_summary['playbooks_available']} playbooks available")
    logger.info(f"VPN Management: {vpn_stats['active_connections']} active connections")
    logger.info(f"Backup & Failover: {backup_status['total_backups']} backups, {backup_status['failover_configs']} failover configs")
    
    logger.info("\n" + "=" * 60)
    logger.info("Secure IT Infrastructure - Starlink System Ready")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
