"""
Advanced SESF Integration Example

Demonstrates integration of all SESF modules in a realistic
Starlink infrastructure security scenario.
"""

import sys
import os
from datetime import datetime

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


class StarlinkSecurityManager:
    """
    Example security manager for Starlink infrastructure.
    Integrates all SESF modules for comprehensive security.
    """
    
    def __init__(self, config_path=None):
        """Initialize the security manager."""
        self.config = SESFConfig(config_path)
        self.framework = SESFFramework(self.config.to_dict())
        
        # Initialize modules
        self.auth = AuthenticationModule(self.config.get('authentication'))
        self.encryption = EncryptionModule(self.config.get('security'))
        self.network = NetworkSecurityModule(self.config.get('network'))
        self.monitoring = MonitoringModule(self.config.get('monitoring'))
        self.compliance = ComplianceModule(self.config.get('compliance'))
        
        self.framework.initialize()
        self._setup_security_policies()
    
    def _setup_security_policies(self):
        """Configure security policies."""
        # Firewall rules for Starlink operations
        self.network.add_firewall_rule({
            "action": "allow",
            "protocol": "HTTPS",
            "port": 443,
            "description": "Allow HTTPS for web interface"
        })
        
        self.network.add_firewall_rule({
            "action": "allow",
            "protocol": "SSH",
            "port": 22,
            "description": "Allow SSH for administration"
        })
        
        self.network.add_firewall_rule({
            "action": "allow",
            "protocol": "Starlink-Proprietary",
            "port": 9000,
            "description": "Allow Starlink satellite communications"
        })
    
    def process_user_login(self, username, password, mfa_token=None):
        """
        Process user login with full security checks.
        """
        print(f"\n--- Processing login for {username} ---")
        
        # Log attempt
        self.monitoring.log_event("authentication", {
            "user": username,
            "action": "login_attempt",
            "timestamp": datetime.now().isoformat()
        }, "INFO")
        
        # Authenticate
        result = self.auth.authenticate(username, password, mfa_token)
        
        if result["success"]:
            # Log success
            self.monitoring.log_event("authentication", {
                "user": username,
                "action": "login_success"
            }, "INFO")
            self.monitoring.update_metric("authentication_success")
            
            # Audit log
            self.compliance.log_audit_event({
                "user": username,
                "action": "user_login",
                "resource": "authentication_system",
                "result": "success",
                "ip_address": "10.0.0.1"
            })
            
            print(f"✓ Login successful for {username}")
            return result
        else:
            # Log failure
            self.monitoring.log_event("authentication", {
                "user": username,
                "action": "login_failed",
                "reason": result["message"]
            }, "WARNING")
            self.monitoring.update_metric("authentication_failure")
            
            print(f"✗ Login failed: {result['message']}")
            return result
    
    def secure_satellite_data(self, data, satellite_id):
        """
        Encrypt satellite telemetry data.
        """
        print(f"\n--- Securing data from satellite {satellite_id} ---")
        
        # Encrypt data
        encrypted = self.encryption.encrypt(data.encode())
        
        # Log operation
        self.monitoring.log_event("encryption", {
            "operation": "encrypt",
            "satellite_id": satellite_id,
            "key_id": encrypted['key_id']
        }, "INFO")
        self.monitoring.update_metric("encryption_operations")
        
        # Audit log
        self.compliance.log_audit_event({
            "user": "system",
            "action": "data_encryption",
            "resource": f"satellite_{satellite_id}_telemetry",
            "result": "success"
        })
        
        print(f"✓ Data encrypted with key {encrypted['key_id']}")
        return encrypted
    
    def check_network_traffic(self, source_ip, dest_ip, protocol, port):
        """
        Validate network traffic against security policies.
        """
        print(f"\n--- Checking traffic: {source_ip} -> {dest_ip}:{port} ({protocol}) ---")
        
        # Rate limiting check
        rate_check = self.network.check_rate_limit(source_ip)
        if not rate_check["allowed"]:
            print(f"✗ Rate limit exceeded: {rate_check['count']}/{rate_check['limit']}")
            self.monitoring.log_event("network", {
                "source_ip": source_ip,
                "action": "rate_limit_exceeded"
            }, "WARNING")
            return False
        
        # Firewall check
        fw_result = self.network.check_firewall(source_ip, dest_ip, protocol, port)
        
        if fw_result["allowed"]:
            print(f"✓ Traffic allowed: {fw_result['reason']}")
            self.monitoring.update_metric("requests_total")
        else:
            print(f"✗ Traffic blocked: {fw_result['reason']}")
            self.monitoring.update_metric("requests_blocked")
            self.monitoring.log_event("network", {
                "source_ip": source_ip,
                "dest_ip": dest_ip,
                "protocol": protocol,
                "port": port,
                "action": "blocked"
            }, "WARNING")
        
        return fw_result["allowed"]
    
    def detect_security_threat(self, event_data):
        """
        Analyze event for security threats.
        """
        print(f"\n--- Analyzing potential security threat ---")
        
        result = self.network.detect_intrusion(event_data)
        
        if result["threat_detected"]:
            print(f"⚠ THREAT DETECTED!")
            print(f"   Threat score: {result['threat_score']}")
            print(f"   Threats: {', '.join(result['threats'])}")
            print(f"   Action: {result['action_taken']}")
            
            # Log critical event
            self.monitoring.log_event("intrusion", {
                "threat_score": result['threat_score'],
                "threats": result['threats'],
                "action": result['action_taken']
            }, "CRITICAL")
            self.monitoring.update_metric("intrusion_attempts")
            
            # Report violation
            self.compliance.report_violation({
                "standard": "NIST",
                "control": "DE.CM-1",
                "description": f"Intrusion attempt detected: {result['threats']}",
                "severity": "HIGH",
                "remediation": "Investigate and remediate immediately"
            })
        else:
            print("✓ No threats detected")
        
        return result
    
    def generate_security_report(self):
        """
        Generate comprehensive security report.
        """
        print("\n" + "=" * 60)
        print("STARLINK SECURITY REPORT")
        print("=" * 60)
        
        # Framework status
        status = self.framework.get_status()
        print(f"\nFramework Status: {'Active' if status['initialized'] else 'Inactive'}")
        print(f"Start Time: {status['start_time']}")
        
        # Monitoring metrics
        print("\nSecurity Metrics:")
        metrics = self.monitoring.get_metrics()
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")
        
        # Network security
        print("\nNetwork Security:")
        net_status = self.network.get_security_status()
        print(f"  Firewall: {'Enabled' if net_status['firewall_enabled'] else 'Disabled'}")
        print(f"  Active Rules: {net_status['firewall_rules']}")
        print(f"  Blocked IPs: {net_status['blocked_ips']}")
        print(f"  Intrusion Attempts: {net_status['intrusion_attempts']}")
        
        # Compliance
        print("\nCompliance Status:")
        comp_report = self.compliance.generate_compliance_report()
        for standard, status in comp_report['compliance_status'].items():
            status_icon = "✓" if status['compliant'] else "✗"
            print(f"  {status_icon} {standard}: {status['passed']}/{status['passed'] + status['failed']} checks passed")
        
        print(f"\nAudit Logs: {comp_report['audit_logs_count']}")
        print(f"Open Violations: {comp_report['open_violations']}")
        
        # Alerts
        print("\nActive Alerts:")
        alerts = self.monitoring.get_alerts(status="open")
        if alerts:
            for alert in alerts[:5]:  # Show top 5
                print(f"  [{alert['level']}] {alert['message']}")
        else:
            print("  No active alerts")
        
        print("\n" + "=" * 60)


def main():
    """Run the advanced integration example."""
    print("SESF Advanced Integration Example - Starlink Security Manager")
    print("=" * 60)
    
    # Initialize security manager
    manager = StarlinkSecurityManager()
    
    # Scenario 1: User login
    manager.process_user_login("operator@starlink.com", "SecurePass123!", "654321")
    
    # Scenario 2: Secure satellite data
    telemetry_data = "SAT-001: lat=45.5231, lon=-122.6765, alt=550km, speed=7.8km/s"
    manager.secure_satellite_data(telemetry_data, "SAT-001")
    
    # Scenario 3: Network traffic validation
    manager.check_network_traffic("10.0.0.50", "192.168.1.100", "HTTPS", 443)
    manager.check_network_traffic("10.0.0.50", "192.168.1.100", "HTTP", 80)  # Should block
    
    # Scenario 4: Detect intrusion
    suspicious_event = {
        "source_ip": "203.0.113.42",
        "failed_auth_attempts": 10,
        "port_scan_detected": True
    }
    manager.detect_security_threat(suspicious_event)
    
    # Scenario 5: Generate report
    manager.generate_security_report()
    
    print("\n✓ Advanced integration example completed!")


if __name__ == "__main__":
    main()
