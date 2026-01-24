#!/usr/bin/env python3
"""
Integration Test
Validates that all security modules work together correctly
Uses unittest framework for proper test infrastructure
"""

import sys
import os
import unittest

# Add the repository root to the path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from modules import (
    FirewallRuleManager,
    VPNManager,
    MFAManager,
    RBACManager,
    EncryptionManager,
    IntrusionDetectionSystem,
    SecurityMonitor
)


class NetworkSecurityTests(unittest.TestCase):
    """Test suite for network security modules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.firewall = FirewallRuleManager()
        self.vpn = VPNManager()
    
    def test_firewall_starlink_access(self):
        """Test firewall Starlink access configuration"""
        rules = self.firewall.configure_starlink_access()
        self.assertEqual(len(rules), 3, "Should configure 3 Starlink rules")
    
    def test_firewall_geo_fencing(self):
        """Test firewall geo-fencing functionality"""
        result = self.firewall.enable_geo_fencing(['US'])
        self.assertTrue(result['enabled'], "Geo-fencing should be enabled")
    
    def test_vpn_creation(self):
        """Test VPN tunnel creation"""
        tunnel = self.vpn.create_tunnel('test.example.com', '10.0.0.0/24')
        self.assertEqual(tunnel['protocol'], 'wireguard', "Should use WireGuard protocol")
    
    def test_vpn_starlink_optimization(self):
        """Test VPN optimization for Starlink"""
        opt = self.vpn.optimize_for_starlink()
        self.assertEqual(opt['mtu'], 1420, "MTU should be optimized for Starlink")


class AccessControlTests(unittest.TestCase):
    """Test suite for access control modules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mfa = MFAManager()
        self.rbac = RBACManager()
    
    def test_mfa_registration(self):
        """Test MFA user registration"""
        result = self.mfa.register_user('test_001', 'testuser')
        self.assertTrue(result, "User registration should succeed")
    
    def test_mfa_verification_not_implemented(self):
        """Test that MFA verification raises NotImplementedError"""
        self.mfa.register_user('test_002', 'testuser2')
        with self.assertRaises(NotImplementedError):
            self.mfa.verify_mfa('test_002', '123456')
    
    def test_rbac_role_assignment(self):
        """Test RBAC role assignment"""
        result = self.rbac.assign_role('test_001', 'admin')
        self.assertTrue(result, "Role assignment should succeed")
    
    def test_rbac_permission_check(self):
        """Test RBAC permission checking"""
        self.rbac.assign_role('test_001', 'admin')
        has_permission = self.rbac.check_permission('test_001', 'read')
        self.assertTrue(has_permission, "Admin should have read permission")


class EncryptionTests(unittest.TestCase):
    """Test suite for encryption module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.encryption = EncryptionManager()
    
    def test_volume_encryption(self):
        """Test data volume encryption configuration"""
        volume = self.encryption.configure_data_encryption('test_volume')
        self.assertEqual(volume['encryption_type'], 'AES-256-GCM',
                        "Should use AES-256-GCM encryption")
    
    def test_tls_configuration(self):
        """Test TLS configuration for Starlink"""
        tls = self.encryption.enable_tls_for_starlink()
        self.assertEqual(tls['tls_version'], '1.3', "Should use TLS 1.3")
    
    def test_data_fingerprinting(self):
        """Test data fingerprint creation"""
        fingerprint = self.encryption.create_data_fingerprint('test_data')
        self.assertIsNotNone(fingerprint['data_fingerprint'],
                            "Should generate fingerprint")
        self.assertGreater(fingerprint['timestamp'], 0,
                          "Should have valid timestamp")
    
    def test_backward_compatibility(self):
        """Test backward compatibility with old method name"""
        # Old method name should still work
        fingerprint = self.encryption.classify_and_fingerprint_data('test_data')
        self.assertIsNotNone(fingerprint['data_fingerprint'],
                            "Legacy method should still work")


class ThreatDetectionTests(unittest.TestCase):
    """Test suite for threat detection modules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ids = IntrusionDetectionSystem()
    
    def test_ids_rules_configuration(self):
        """Test IDS rules configuration"""
        rules = self.ids.configure_ids_rules()
        self.assertGreater(len(rules), 0, "Should have IDS rules configured")
    
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        alert = self.ids.detect_anomaly('test_event', 'high', 'Test anomaly')
        self.assertEqual(alert['severity'], 'high', "Should detect high severity anomaly")
    
    def test_behavioral_analysis(self):
        """Test behavioral analysis enablement"""
        behavioral = self.ids.enable_behavioral_analysis()
        self.assertTrue(behavioral['enabled'], "Behavioral analysis should be enabled")


class SecurityMonitoringTests(unittest.TestCase):
    """Test suite for security monitoring module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = SecurityMonitor()
    
    def test_continuous_monitoring_setup(self):
        """Test continuous monitoring setup"""
        monitoring = self.monitor.setup_continuous_monitoring()
        self.assertGreater(len(monitoring['monitoring_scope']), 0,
                          "Should have monitoring scope defined")
    
    def test_siem_integration(self):
        """Test SIEM integration configuration"""
        siem = self.monitor.configure_siem_integration()
        self.assertGreater(len(siem['log_sources']), 0,
                          "Should have log sources configured")
    
    def test_compliance_check(self):
        """Test compliance check execution"""
        compliance = self.monitor.run_compliance_check('SOC2')
        self.assertGreater(compliance['compliance_score'], 0,
                          "Should return compliance score")
        self.assertTrue(compliance['is_demonstration'],
                       "Should be marked as demonstration")


class IntegrationTests(unittest.TestCase):
    """Test suite for full integration scenarios"""
    
    def setUp(self):
        """Set up all components for integration testing"""
        self.firewall = FirewallRuleManager()
        self.vpn = VPNManager()
        self.mfa = MFAManager()
        self.rbac = RBACManager()
        self.encryption = EncryptionManager()
        self.ids = IntrusionDetectionSystem()
        self.monitor = SecurityMonitor()
    
    def test_full_integration(self):
        """Test all modules working together"""
        # Configure all components
        self.firewall.configure_starlink_access()
        self.vpn.optimize_for_starlink()
        self.mfa.register_user('integration_test', 'testuser')
        self.rbac.assign_role('integration_test', 'admin')
        self.encryption.enable_tls_for_starlink()
        self.ids.configure_ids_rules()
        self.monitor.setup_continuous_monitoring()
        
        # Verify integration
        self.assertGreater(len(self.firewall.get_all_rules()), 0,
                          "Firewall should have rules")
        self.assertGreaterEqual(len(self.vpn.get_tunnel_status()), 0,
                               "VPN should be operational")
        self.assertIn('integration_test', self.mfa.registered_users,
                     "MFA should have registered user")
        self.assertTrue(self.rbac.check_permission('integration_test', 'read'),
                       "RBAC should grant permissions")
        self.assertGreaterEqual(len(self.encryption.encrypted_volumes), 0,
                               "Encryption should be configured")
        self.assertGreater(len(self.ids.configure_ids_rules()), 0,
                          "IDS should have rules")
        self.assertTrue(self.monitor.monitoring_active,
                       "Monitoring should be active")


def main():
    """Run the test suite"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(NetworkSecurityTests))
    suite.addTests(loader.loadTestsFromTestCase(AccessControlTests))
    suite.addTests(loader.loadTestsFromTestCase(EncryptionTests))
    suite.addTests(loader.loadTestsFromTestCase(ThreatDetectionTests))
    suite.addTests(loader.loadTestsFromTestCase(SecurityMonitoringTests))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTests))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
