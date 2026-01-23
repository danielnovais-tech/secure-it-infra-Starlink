#!/usr/bin/env python3
"""
Validation Tests
Tests for input validation and security improvements from code review feedback
"""

import sys
import os
import unittest

# Add the repository root to the path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from modules import (
    FirewallRuleManager,
    MFAManager,
    RBACManager,
    IntrusionDetectionSystem,
    SecurityMonitor
)


class FirewallValidationTests(unittest.TestCase):
    """Test firewall input validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.firewall = FirewallRuleManager()
    
    def test_valid_port_number(self):
        """Test valid port numbers are accepted"""
        # Should not raise
        rule = self.firewall.add_rule('inbound', '192.168.1.0/24', 'internal_network', 80)
        self.assertEqual(rule['port'], 80)
        
        rule = self.firewall.add_rule('inbound', '192.168.1.0/24', 'internal_network', 65535)
        self.assertEqual(rule['port'], 65535)
    
    def test_wildcard_port(self):
        """Test wildcard port is accepted"""
        rule = self.firewall.add_rule('inbound', '192.168.1.0/24', 'internal_network', '*')
        self.assertEqual(rule['port'], '*')
    
    def test_invalid_port_too_low(self):
        """Test port validation rejects ports below 1"""
        with self.assertRaises(ValueError) as cm:
            self.firewall.add_rule('inbound', '192.168.1.0/24', 'internal_network', 0)
        self.assertIn('1-65535', str(cm.exception))
    
    def test_invalid_port_too_high(self):
        """Test port validation rejects ports above 65535"""
        with self.assertRaises(ValueError) as cm:
            self.firewall.add_rule('inbound', '192.168.1.0/24', 'internal_network', 65536)
        self.assertIn('1-65535', str(cm.exception))
    
    def test_invalid_port_type(self):
        """Test port validation rejects invalid types"""
        with self.assertRaises(ValueError) as cm:
            self.firewall.add_rule('inbound', '192.168.1.0/24', 'internal_network', 'invalid')
        self.assertIn('Invalid port value', str(cm.exception))
    
    def test_valid_network_identifiers(self):
        """Test valid network identifiers are accepted"""
        valid_identifiers = [
            'internal_network',
            'external_network', 
            'starlink_gateway',
            'dmz',
            'management_network',
            'any'
        ]
        
        for identifier in valid_identifiers:
            rule = self.firewall.add_rule('inbound', identifier, 'internal_network', 443)
            self.assertEqual(rule['source'], identifier)
    
    def test_ip_address_as_network_identifier(self):
        """Test IP addresses are accepted as network identifiers"""
        # IPv4
        rule = self.firewall.add_rule('inbound', '192.168.1.1', 'internal_network', 443)
        self.assertEqual(rule['source'], '192.168.1.1')
        
        # CIDR
        rule = self.firewall.add_rule('inbound', '10.0.0.0/24', 'internal_network', 443)
        self.assertEqual(rule['source'], '10.0.0.0/24')
        
        # IPv6
        rule = self.firewall.add_rule('inbound', '2001:db8::1', 'internal_network', 443)
        self.assertEqual(rule['source'], '2001:db8::1')
    
    def test_invalid_network_identifier(self):
        """Test invalid network identifiers are rejected"""
        with self.assertRaises(ValueError) as cm:
            self.firewall.add_rule('inbound', 'invalid_network', 'internal_network', 443)
        self.assertIn('Invalid source', str(cm.exception))
        self.assertIn('internal_network', str(cm.exception))  # Should suggest valid values


class IDSConfigurationTests(unittest.TestCase):
    """Test IDS configuration and baseline detection"""
    
    def test_default_threshold(self):
        """Test default connection threshold"""
        ids = IntrusionDetectionSystem()
        self.assertEqual(ids.connection_threshold, 10000)
    
    def test_custom_threshold(self):
        """Test custom connection threshold"""
        ids = IntrusionDetectionSystem(connection_threshold=5000)
        self.assertEqual(ids.connection_threshold, 5000)
    
    def test_baseline_multiplier(self):
        """Test baseline multiplier configuration"""
        ids = IntrusionDetectionSystem(baseline_multiplier=3.0)
        self.assertEqual(ids.baseline_multiplier, 3.0)
    
    def test_static_threshold_detection(self):
        """Test traffic analysis with static threshold"""
        ids = IntrusionDetectionSystem(connection_threshold=100)
        
        # Below threshold - should be low
        result = ids.analyze_traffic_patterns([i for i in range(50)])
        self.assertEqual(result['threat_level'], 'low')
        self.assertEqual(len(result['suspicious_patterns']), 0)
        
        # Above threshold - should be medium
        result = ids.analyze_traffic_patterns([i for i in range(150)])
        self.assertEqual(result['threat_level'], 'medium')
        self.assertGreater(len(result['suspicious_patterns']), 0)
    
    def test_baseline_detection(self):
        """Test baseline-based anomaly detection"""
        ids = IntrusionDetectionSystem(baseline_multiplier=2.0)
        
        # Set baseline to 100 connections
        ids.set_traffic_baseline(100)
        self.assertEqual(ids.traffic_baseline, 100)
        
        # Below baseline threshold (100 * 2.0 = 200) - should be low
        result = ids.analyze_traffic_patterns([i for i in range(150)])
        self.assertEqual(result['threat_level'], 'low')
        
        # Above baseline threshold - should be medium
        result = ids.analyze_traffic_patterns([i for i in range(250)])
        self.assertEqual(result['threat_level'], 'medium')
        self.assertIn('baseline', result['suspicious_patterns'][0].lower())


class MFASecurityTests(unittest.TestCase):
    """Test MFA security improvements"""
    
    def test_secure_secret_generation(self):
        """Test TOTP secret uses secure random generation"""
        mfa = MFAManager()
        mfa.register_user('user1', 'test')
        
        # Generate multiple secrets - they should be different (not predictable)
        secret1 = mfa.generate_totp_secret('user1')
        
        mfa.register_user('user2', 'test')
        secret2 = mfa.generate_totp_secret('user2')
        
        self.assertNotEqual(secret1, secret2, "Secrets should be unique")
        self.assertEqual(len(secret1), 32, "Secret should be 32 characters")
        self.assertEqual(len(secret2), 32, "Secret should be 32 characters")
    
    def test_mfa_verification_raises_not_implemented(self):
        """Test MFA verification properly raises NotImplementedError"""
        mfa = MFAManager()
        mfa.register_user('user1', 'test')
        
        with self.assertRaises(NotImplementedError) as cm:
            mfa.verify_mfa('user1', '123456')
        
        self.assertIn('TOTP', str(cm.exception))
        self.assertIn('pyotp', str(cm.exception))


class ComplianceCheckTests(unittest.TestCase):
    """Test compliance check demonstration markers"""
    
    def test_compliance_demonstration_marker(self):
        """Test compliance check is properly marked as demonstration"""
        monitor = SecurityMonitor()
        result = monitor.run_compliance_check('SOC2')
        
        self.assertTrue(result['is_demonstration'],
                       "Should be marked as demonstration")
        self.assertIn('note', result)
        self.assertIn('Demonstration', result['note'])
        self.assertGreater(len(result['findings']), 0)
        
        # Check findings include demonstration notice
        demo_finding = result['findings'][0]
        self.assertEqual(demo_finding['type'], 'demonstration')


class RBACLoggingTests(unittest.TestCase):
    """Test RBAC logging functionality"""
    
    def test_role_assignment_success(self):
        """Test successful role assignment"""
        rbac = RBACManager()
        # Should not raise and should log
        result = rbac.assign_role('user1', 'admin')
        self.assertTrue(result)
    
    def test_role_assignment_failure_logging(self):
        """Test failed role assignment raises and would log"""
        rbac = RBACManager()
        
        with self.assertRaises(ValueError) as cm:
            rbac.assign_role('user1', 'nonexistent_role')
        
        self.assertIn('does not exist', str(cm.exception))
    
    def test_permission_check_logging(self):
        """Test permission checks (both success and failure)"""
        rbac = RBACManager()
        
        # Test failed permission check (no roles assigned)
        result = rbac.check_permission('user1', 'read')
        self.assertFalse(result)
        
        # Test successful permission check
        rbac.assign_role('user1', 'admin')
        result = rbac.check_permission('user1', 'read')
        self.assertTrue(result)
        
        # Test denied permission check (user has role but not this permission)
        result = rbac.check_permission('user1', 'nonexistent_permission')
        self.assertFalse(result)


def main():
    """Run validation tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(FirewallValidationTests))
    suite.addTests(loader.loadTestsFromTestCase(IDSConfigurationTests))
    suite.addTests(loader.loadTestsFromTestCase(MFASecurityTests))
    suite.addTests(loader.loadTestsFromTestCase(ComplianceCheckTests))
    suite.addTests(loader.loadTestsFromTestCase(RBACLoggingTests))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
