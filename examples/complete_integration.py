#!/usr/bin/env python3
"""
Example: Complete Security Toolkit Integration
Demonstrates all security components working together.
"""

from secure_it_starlink.network import NetworkMonitor, ConnectionValidator
from secure_it_starlink.crypto import EncryptionManager, KeyManager
from secure_it_starlink.logging import SecurityLogger, AlertManager, AlertSeverity
from secure_it_starlink.scanning import VulnerabilityScanner
from secure_it_starlink.access import AccessController, AuthenticationManager
from secure_it_starlink.config import SecurityConfig


def main():
    print("=" * 80)
    print("Secure IT Starlink - Complete Security Toolkit Integration")
    print("=" * 80)
    print()

    # Initialize all components
    print("Initializing Security Infrastructure...")
    print("-" * 80)
    
    security_config = SecurityConfig()
    logger = SecurityLogger()
    alert_manager = AlertManager()
    network_monitor = NetworkMonitor()
    connection_validator = ConnectionValidator()
    encryption_manager = EncryptionManager()
    key_manager = KeyManager()
    vuln_scanner = VulnerabilityScanner()
    access_controller = AccessController()
    auth_manager = AuthenticationManager()
    
    print("✓ All security components initialized\n")

    # 1. Access Control Setup
    print("1. Setting Up Access Control")
    print("-" * 80)
    
    # Create users
    auth_manager.create_user("admin", "SecureAdminP@ss123", roles=["administrator"])
    auth_manager.create_user("operator", "SecureOperP@ss123", roles=["operator"])
    logger.info("Created user accounts", {"users": ["admin", "operator"]})
    
    # Create access policies
    access_controller.create_policy(
        "admin-full-access",
        resource="starlink-infrastructure",
        allowed_actions=["read", "write", "delete", "configure"],
        principals=["admin"]
    )
    access_controller.create_policy(
        "operator-read-access",
        resource="starlink-infrastructure",
        allowed_actions=["read", "monitor"],
        principals=["operator"]
    )
    logger.info("Access policies created")
    print("✓ Users and access policies configured\n")

    # 2. Authentication
    print("2. User Authentication")
    print("-" * 80)
    
    admin_token = auth_manager.authenticate("admin", "SecureAdminP@ss123")
    if admin_token:
        print("✓ Admin authenticated successfully")
        logger.info("Admin login successful", {"username": "admin"})
    
    # Validate session
    username = auth_manager.validate_session(admin_token)
    print(f"✓ Session validated for user: {username}\n")

    # 3. Encryption Setup
    print("3. Setting Up Encryption")
    print("-" * 80)
    
    # Generate encryption keys
    key_manager.generate_key("data-encryption-key", "symmetric")
    key_manager.generate_key("communication-key", "symmetric")
    print(f"✓ Generated encryption keys: {len(key_manager.list_keys())} keys")
    
    # Encrypt sensitive data
    sensitive_data = "Starlink terminal configuration data"
    encrypted_data = encryption_manager.encrypt(sensitive_data)
    print(f"✓ Data encrypted: {len(encrypted_data)} bytes")
    logger.info("Sensitive data encrypted", {"data_type": "configuration"})


    # 4. Network Security
    print("\n4. Network Security Monitoring")
    print("-" * 80)
    
    network_monitor.start_monitoring()
    
    # Validate connections
    connection = connection_validator.validate_connection("192.168.1.100", "starlink.com")
    if connection['valid']:
        print("✓ Connection validation passed")
    
    # Check network health
    health = network_monitor.check_connection_health("8.8.8.8")
    if health['status'] == 'healthy':
        print(f"✓ Network health check passed (latency: {health.get('latency_ms', 'N/A')}ms)")
        logger.info("Network health check completed", health)
    else:
        logger.warning("Network health check failed", health)
        alert_manager.create_alert(
            AlertSeverity.HIGH,
            "Network Health Issue",
            "Network connection health check failed",
            health
        )
    print()

    # 5. Security Scanning
    print("5. Security Assessment")
    print("-" * 80)
    
    # Validate configuration
    config_validation = security_config.validate()
    print(f"Configuration checks: {config_validation['passed_checks']}/{config_validation['total_checks']} passed")
    
    # Scan for vulnerabilities
    test_config = security_config.get_config()
    vuln_results = vuln_scanner.scan_configuration(test_config)
    print(f"Vulnerability scan: {vuln_results['vulnerabilities_found']} issues found")
    
    if vuln_results['vulnerabilities_found'] > 0:
        alert_manager.create_alert(
            AlertSeverity.CRITICAL,
            "Vulnerabilities Detected",
            f"Found {vuln_results['vulnerabilities_found']} security vulnerabilities",
            vuln_results
        )
    print()

    # 6. Security Dashboard Summary
    print("6. Security Dashboard Summary")
    print("-" * 80)
    
    print("\nAuthentication:")
    print(f"  Total users: {len(auth_manager.users)}")
    print(f"  Active sessions: {len([s for s in auth_manager.sessions.values() if s['status'] == 'active'])}")
    
    print("\nAccess Control:")
    print(f"  Total policies: {len(access_controller.access_policies)}")
    print(f"  Access checks: {len(access_controller.access_logs)}")
    
    print("\nEncryption:")
    print(f"  Active keys: {len(key_manager.list_keys(status='active'))}")
    print(f"  Encryption operations: {len(encryption_manager.operations_log)}")
    
    print("\nNetwork Monitoring:")
    stats = network_monitor.get_connection_stats()
    print(f"  Health checks: {stats['total_checks']}")
    print(f"  Health ratio: {stats['health_ratio']:.2%}")
    
    print("\nAlerts:")
    alert_stats = alert_manager.get_alert_stats()
    print(f"  Total alerts: {alert_stats['total_alerts']}")
    print(f"  Active alerts: {alert_stats['active_alerts']}")
    
    print("\nSecurity Logs:")
    print(f"  Total log entries: {len(logger.get_logs())}")
    
    # 7. Cleanup
    print("\n7. Cleanup and Shutdown")
    print("-" * 80)
    
    network_monitor.stop_monitoring()
    auth_manager.logout(admin_token)
    logger.info("Security infrastructure shutdown completed")
    print("✓ All components shut down cleanly")
    
    print("\n" + "=" * 80)
    print("Complete security toolkit integration demonstration completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
