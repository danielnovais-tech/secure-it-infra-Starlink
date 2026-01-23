"""
Integration tests for SESF Framework

Tests the integration of all modules working together.
"""

import unittest
from sesf import SESFFramework, SESFConfig
from sesf.modules import (
    AuthenticationModule,
    EncryptionModule,
    NetworkSecurityModule,
    MonitoringModule,
    ComplianceModule
)


class TestSESFIntegration(unittest.TestCase):
    """Integration test cases for SESF."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = SESFConfig()
        self.framework = SESFFramework(self.config.to_dict())
    
    def test_full_framework_initialization(self):
        """Test complete framework initialization."""
        result = self.framework.initialize()
        self.assertTrue(result)
        
        status = self.framework.get_status()
        self.assertEqual(len(status['modules']), 5)
    
    def test_authentication_with_monitoring(self):
        """Test authentication with monitoring integration."""
        auth = AuthenticationModule(self.config.get('authentication'))
        monitoring = MonitoringModule(self.config.get('monitoring'))
        
        # Authenticate
        result = auth.authenticate("test@example.com", "password", "123456")
        
        # Log authentication event
        monitoring.log_event("authentication", {
            "user": "test@example.com",
            "success": result["success"]
        }, "INFO")
        
        # Check metrics
        monitoring.update_metric("authentication_success")
        metrics = monitoring.get_metrics()
        
        self.assertGreater(metrics["authentication_success"], 0)
    
    def test_encryption_with_compliance(self):
        """Test encryption with compliance logging."""
        encryption = EncryptionModule(self.config.get('security'))
        compliance = ComplianceModule(self.config.get('compliance'))
        
        # Encrypt data
        data = b"Sensitive data"
        encrypted = encryption.encrypt(data)
        
        # Log compliance event
        compliance.log_audit_event({
            "user": "system",
            "action": "data_encryption",
            "resource": "sensitive_data",
            "result": "success",
            "details": {"key_id": encrypted['key_id']}
        })
        
        # Check audit logs
        logs = compliance.get_audit_logs(action="data_encryption")
        self.assertGreater(len(logs), 0)
    
    def test_network_security_with_monitoring(self):
        """Test network security with monitoring."""
        network = NetworkSecurityModule(self.config.get('network'))
        monitoring = MonitoringModule(self.config.get('monitoring'))
        
        # Block suspicious IP
        suspicious_ip = "203.0.113.42"
        network.block_ip(suspicious_ip, "Suspicious activity")
        
        # Log security event
        monitoring.log_event("network_security", {
            "ip": suspicious_ip,
            "action": "blocked"
        }, "WARNING")
        
        # Check that IP is blocked
        result = network.check_firewall(suspicious_ip, "10.0.0.1", "HTTPS", 443)
        self.assertFalse(result["allowed"])
    
    def test_compliance_checks(self):
        """Test compliance checking."""
        compliance = ComplianceModule(self.config.get('compliance'))
        
        # Check multiple standards
        for standard in ["ISO27001", "SOC2", "NIST"]:
            result = compliance.check_compliance(standard)
            self.assertIn("compliant", result)
            self.assertIn("checks_performed", result)
    
    def test_end_to_end_scenario(self):
        """Test complete end-to-end security scenario."""
        # Initialize all modules
        auth = AuthenticationModule(self.config.get('authentication'))
        encryption = EncryptionModule(self.config.get('security'))
        network = NetworkSecurityModule(self.config.get('network'))
        monitoring = MonitoringModule(self.config.get('monitoring'))
        compliance = ComplianceModule(self.config.get('compliance'))
        
        # Step 1: Authenticate user
        auth_result = auth.authenticate("operator@starlink.com", "password", "123456")
        self.assertTrue(auth_result["success"])
        
        # Step 2: Check network access
        network.check_firewall("10.0.0.1", "192.168.1.1", "HTTPS", 443)
        monitoring.log_event("network", {"access": "granted"}, "INFO")
        
        # Step 3: Encrypt sensitive data
        data = b"Satellite telemetry data"
        encryption.encrypt(data)
        monitoring.log_event("encryption", {"operation": "encrypt"}, "INFO")
        
        # Step 4: Compliance logging
        compliance.log_audit_event({
            "user": "operator@starlink.com",
            "action": "data_access",
            "resource": "satellite_telemetry",
            "result": "success"
        })
        
        # Step 5: Generate reports
        monitoring_report = monitoring.generate_report("24h")
        compliance_report = compliance.generate_compliance_report()
        
        # Verify reports
        self.assertIn("metrics", monitoring_report)
        self.assertIn("compliance_status", compliance_report)


if __name__ == "__main__":
    unittest.main()
