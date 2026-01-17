"""
Basic SESF Usage Example

This example demonstrates basic initialization and usage of the
Starlink Enterprise Security Framework.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sesf import SESFFramework, SESFConfig
from sesf.modules import (
    AuthenticationModule,
    EncryptionModule,
    NetworkSecurityModule,
    MonitoringModule,
    ComplianceModule
)


def main():
    print("=" * 60)
    print("SESF - Starlink Enterprise Security Framework")
    print("Basic Usage Example")
    print("=" * 60)
    
    # 1. Initialize Configuration
    print("\n1. Initializing Configuration...")
    config = SESFConfig()
    print(f"   Environment: {config.get('framework.environment')}")
    print(f"   Encryption: {config.get('security.encryption_algorithm')}")
    
    # 2. Initialize Framework
    print("\n2. Initializing SESF Framework...")
    framework = SESFFramework(config.to_dict())
    if framework.initialize():
        print("   ✓ Framework initialized successfully")
    
    # 3. Get Framework Status
    print("\n3. Framework Status:")
    status = framework.get_status()
    print(f"   Initialized: {status['initialized']}")
    print(f"   Version: {status['version']}")
    print(f"   Modules loaded: {len(status['modules'])}")
    for module_name in status['modules']:
        print(f"     - {module_name}")
    
    # 4. Authentication Example
    print("\n4. Authentication Example:")
    auth = AuthenticationModule(config.get('authentication'))
    result = auth.authenticate("admin@starlink.example", "SecurePass123!", "123456")
    if result["success"]:
        print(f"   ✓ User authenticated")
        print(f"   Session token: {result['session_token'][:20]}...")
    
    # 5. Encryption Example
    print("\n5. Encryption Example:")
    encryption = EncryptionModule(config.get('security'))
    data = b"Starlink satellite telemetry: position=45.5N,122.6W"
    encrypted = encryption.encrypt(data)
    print(f"   ✓ Data encrypted")
    print(f"   Key ID: {encrypted['key_id']}")
    print(f"   Algorithm: {encrypted['algorithm']}")
    
    # 6. Network Security Example
    print("\n6. Network Security Example:")
    network = NetworkSecurityModule(config.get('network'))
    
    # Add firewall rule
    network.add_firewall_rule({
        "action": "allow",
        "protocol": "HTTPS",
        "port": 443
    })
    
    # Check traffic
    check_result = network.check_firewall("10.0.0.1", "192.168.1.100", "HTTPS", 443)
    print(f"   Firewall check: {check_result['allowed']}")
    print(f"   Reason: {check_result['reason']}")
    
    # Rate limiting check
    rate_check = network.check_rate_limit("10.0.0.1", limit=100, window_seconds=60)
    print(f"   Rate limit: {rate_check['count']}/{rate_check['limit']} requests")
    
    # 7. Monitoring Example
    print("\n7. Monitoring Example:")
    monitoring = MonitoringModule(config.get('monitoring'))
    
    # Log events
    monitoring.log_event("authentication", {"user": "admin", "action": "login"}, "INFO")
    monitoring.log_event("network", {"blocked_ip": "192.168.1.200"}, "WARNING")
    
    # Update metrics
    monitoring.update_metric("requests_total", 1)
    monitoring.update_metric("authentication_success", 1)
    
    # Get metrics
    metrics = monitoring.get_metrics()
    print(f"   Total requests: {metrics['requests_total']}")
    print(f"   Auth success: {metrics['authentication_success']}")
    
    # Generate report
    report = monitoring.generate_report("24h")
    print(f"   Status: {report['summary']}")
    
    # 8. Compliance Example
    print("\n8. Compliance Example:")
    compliance = ComplianceModule(config.get('compliance'))
    
    # Log audit event
    compliance.log_audit_event({
        "user": "admin",
        "action": "system_configuration_change",
        "resource": "firewall_rules",
        "result": "success",
        "ip_address": "10.0.0.1"
    })
    print("   ✓ Audit event logged")
    
    # Check compliance
    for standard in ["ISO27001", "SOC2", "NIST"]:
        result = compliance.check_compliance(standard)
        status_icon = "✓" if result["compliant"] else "✗"
        print(f"   {status_icon} {standard}: {result['passed']}/{result['passed'] + result['failed']} checks passed")
    
    # Generate compliance report
    comp_report = compliance.generate_compliance_report()
    print(f"   Open violations: {comp_report['open_violations']}")
    
    # 9. Shutdown
    print("\n9. Shutting down framework...")
    framework.shutdown()
    print("   ✓ Framework shutdown complete")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
