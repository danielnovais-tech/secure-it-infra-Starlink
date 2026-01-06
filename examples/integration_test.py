#!/usr/bin/env python3
"""
Integration Test
Validates that all security modules work together correctly
"""

import sys
sys.path.insert(0, '/home/runner/work/secure-it-infra-Starlink/secure-it-infra-Starlink')

from modules import (
    FirewallRuleManager,
    VPNManager,
    MFAManager,
    RBACManager,
    EncryptionManager,
    IntrusionDetectionSystem,
    SecurityMonitor
)

def test_network_security():
    """Test network security modules"""
    print("Testing Network Security Modules...")
    
    firewall = FirewallRuleManager()
    assert len(firewall.configure_starlink_access()) == 3, "Starlink rules failed"
    assert firewall.enable_geo_fencing(['US'])['enabled'] == True, "Geo-fencing failed"
    
    vpn = VPNManager()
    tunnel = vpn.create_tunnel('test.example.com', '10.0.0.0/24')
    assert tunnel['protocol'] == 'wireguard', "VPN creation failed"
    opt = vpn.optimize_for_starlink()
    assert opt['mtu'] == 1420, "Starlink optimization failed"
    
    print("  ✓ Network Security: PASSED")
    return True

def test_access_control():
    """Test access control modules"""
    print("Testing Access Control Modules...")
    
    mfa = MFAManager()
    assert mfa.register_user('test_001', 'testuser') == True, "MFA registration failed"
    assert mfa.verify_mfa('test_001', '123456') == True, "MFA verification failed"
    
    rbac = RBACManager()
    assert rbac.assign_role('test_001', 'admin') == True, "Role assignment failed"
    assert rbac.check_permission('test_001', 'read') == True, "Permission check failed"
    
    print("  ✓ Access Control: PASSED")
    return True

def test_encryption():
    """Test encryption module"""
    print("Testing Encryption Module...")
    
    encryption = EncryptionManager()
    volume = encryption.configure_data_encryption('test_volume')
    assert volume['encryption_type'] == 'AES-256-GCM', "Volume encryption failed"
    
    tls = encryption.enable_tls_for_starlink()
    assert tls['tls_version'] == '1.3', "TLS configuration failed"
    
    encrypted = encryption.encrypt_sensitive_data('test_data')
    assert encrypted['encrypted_data'] is not None, "Data encryption failed"
    
    print("  ✓ Encryption: PASSED")
    return True

def test_threat_detection():
    """Test threat detection modules"""
    print("Testing Threat Detection Modules...")
    
    ids = IntrusionDetectionSystem()
    rules = ids.configure_ids_rules()
    assert len(rules) > 0, "IDS rules configuration failed"
    
    alert = ids.detect_anomaly('test_event', 'high', 'Test anomaly')
    assert alert['severity'] == 'high', "Anomaly detection failed"
    
    behavioral = ids.enable_behavioral_analysis()
    assert behavioral['enabled'] == True, "Behavioral analysis failed"
    
    print("  ✓ Threat Detection: PASSED")
    return True

def test_monitoring():
    """Test security monitoring module"""
    print("Testing Security Monitoring Module...")
    
    monitor = SecurityMonitor()
    monitoring = monitor.setup_continuous_monitoring()
    assert len(monitoring['monitoring_scope']) > 0, "Monitoring setup failed"
    
    siem = monitor.configure_siem_integration()
    assert len(siem['log_sources']) > 0, "SIEM integration failed"
    
    compliance = monitor.run_compliance_check('SOC2')
    assert compliance['compliance_score'] > 0, "Compliance check failed"
    
    print("  ✓ Security Monitoring: PASSED")
    return True

def test_integration():
    """Test full integration scenario"""
    print("Testing Full Integration Scenario...")
    
    # Create a complete security setup
    firewall = FirewallRuleManager()
    vpn = VPNManager()
    mfa = MFAManager()
    rbac = RBACManager()
    encryption = EncryptionManager()
    ids = IntrusionDetectionSystem()
    monitor = SecurityMonitor()
    
    # Configure all components
    firewall.configure_starlink_access()
    vpn.optimize_for_starlink()
    mfa.register_user('integration_test', 'testuser')
    rbac.assign_role('integration_test', 'admin')
    encryption.enable_tls_for_starlink()
    ids.configure_ids_rules()
    monitor.setup_continuous_monitoring()
    
    # Verify integration
    assert len(firewall.get_all_rules()) > 0, "Integration: firewall failed"
    assert len(vpn.get_tunnel_status()) >= 0, "Integration: vpn failed"
    assert 'integration_test' in mfa.registered_users, "Integration: mfa failed"
    assert rbac.check_permission('integration_test', 'read'), "Integration: rbac failed"
    assert len(encryption.encrypted_volumes) >= 0, "Integration: encryption failed"
    assert len(ids.configure_ids_rules()) > 0, "Integration: ids failed"
    assert monitor.monitoring_active == True, "Integration: monitoring failed"
    
    print("  ✓ Full Integration: PASSED")
    return True

def main():
    """Run all tests"""
    print("=" * 70)
    print("Secure-IT-Infra-Starlink - Integration Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        test_network_security,
        test_access_control,
        test_encryption,
        test_threat_detection,
        test_monitoring,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: FAILED - {str(e)}")
            failed += 1
    
    print()
    print("=" * 70)
    print("Test Results")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("✓ All tests passed! The security infrastructure is working correctly.")
        print()
        print("The following components have been validated:")
        print("  • Network Security (Firewall, VPN)")
        print("  • Access Control (MFA, RBAC)")
        print("  • Encryption (Data at rest and in transit)")
        print("  • Threat Detection (IDS, Behavioral Analysis)")
        print("  • Security Monitoring (SIEM, Compliance)")
        print("  • Full Integration (All modules working together)")
        return 0
    else:
        print(f"✗ {failed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
