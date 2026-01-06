#!/usr/bin/env python3
"""
Basic Security Setup Example
Demonstrates basic security module usage for Starlink infrastructure
"""

import sys
import os

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

def main():
    """Basic security setup demonstration"""
    
    print("=" * 60)
    print("Secure-IT-Infra-Starlink - Basic Setup Example")
    print("=" * 60)
    print()
    
    # 1. Configure Firewall
    print("1. Configuring Firewall Rules...")
    firewall = FirewallRuleManager()
    
    # Configure Starlink access
    starlink_rules = firewall.configure_starlink_access()
    print(f"   ✓ Added {len(starlink_rules)} Starlink firewall rules")
    
    # Block unauthorized IPs
    blocked = firewall.block_unauthorized_access(['192.168.99.99', '10.99.99.99'])
    print(f"   ✓ Blocked {len(blocked)} unauthorized IP addresses")
    
    # Enable geo-fencing
    geo_config = firewall.enable_geo_fencing(['US', 'CA', 'EU'])
    print(f"   ✓ Geo-fencing enabled for: {geo_config['allowed_regions']}")
    print()
    
    # 2. Configure VPN
    print("2. Configuring VPN...")
    vpn = VPNManager()
    
    # Create VPN tunnel
    tunnel = vpn.create_tunnel(
        endpoint='starlink-remote-site.example.com',
        subnet='10.1.0.0/24',
        bandwidth_limit='100Mbps'
    )
    print(f"   ✓ VPN tunnel created to {tunnel['endpoint']}")
    
    # Optimize for Starlink
    starlink_opt = vpn.optimize_for_starlink()
    print(f"   ✓ Starlink optimization: MTU={starlink_opt['mtu']}, Keepalive={starlink_opt['keepalive']}s")
    print()
    
    # 3. Configure Access Control
    print("3. Configuring Access Control...")
    mfa = MFAManager()
    rbac = RBACManager()
    
    # Register users with MFA
    users = [
        ('user_001', 'alice', 'admin'),
        ('user_002', 'bob', 'security_analyst'),
        ('user_003', 'charlie', 'network_engineer')
    ]
    
    for user_id, username, role in users:
        mfa.register_user(user_id, username, mfa_method='totp')
        secret = mfa.generate_totp_secret(user_id)
        rbac.assign_role(user_id, role)
        print(f"   ✓ User {username} registered with role {role}")
    print()
    
    # 4. Configure Encryption
    print("4. Configuring Encryption...")
    encryption = EncryptionManager()
    
    # Configure data encryption
    volume = encryption.configure_data_encryption('production_volume')
    print(f"   ✓ Volume encryption: {volume['encryption_type']}, Rotation: {volume['rotation_period_days']} days")
    
    # Enable TLS for Starlink
    tls_config = encryption.enable_tls_for_starlink()
    print(f"   ✓ TLS {tls_config['tls_version']} configured with {len(tls_config['cipher_suites'])} cipher suites")
    print()
    
    # 5. Configure Threat Detection
    print("5. Configuring Threat Detection...")
    ids = IntrusionDetectionSystem()
    
    # Configure IDS rules
    ids_rules = ids.configure_ids_rules()
    total_rules = sum(len(rules) for rules in ids_rules.values())
    print(f"   ✓ IDS configured with {total_rules} rule categories")
    
    # Enable behavioral analysis
    behavioral = ids.enable_behavioral_analysis()
    print(f"   ✓ Behavioral analysis enabled with {len(behavioral['ml_models'])} ML models")
    print()
    
    # 6. Configure Monitoring
    print("6. Configuring Security Monitoring...")
    monitor = SecurityMonitor()
    
    # Setup continuous monitoring
    monitoring = monitor.setup_continuous_monitoring()
    print(f"   ✓ Monitoring {len(monitoring['monitoring_scope'])} security areas")
    
    # Configure SIEM integration
    siem = monitor.configure_siem_integration()
    print(f"   ✓ SIEM collecting from {len(siem['log_sources'])} log sources")
    print()
    
    # 7. Run Compliance Check
    print("7. Running Compliance Checks...")
    compliance_frameworks = ['SOC2', 'ISO27001', 'GDPR']
    
    for framework in compliance_frameworks:
        result = monitor.run_compliance_check(framework)
        score = result['compliance_score']
        print(f"   ✓ {framework}: {score:.1f}% compliant ({result['checks_passed']}/{result['checks_passed'] + result['checks_failed']} checks passed)")
    print()
    
    # 8. Summary
    print("=" * 60)
    print("Security Setup Complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  • Firewall Rules: {len(firewall.get_all_rules())}")
    print(f"  • VPN Tunnels: {len(vpn.get_tunnel_status())}")
    print(f"  • Registered Users: {len(users)}")
    print(f"  • Encrypted Volumes: {len(encryption.encrypted_volumes)}")
    print(f"  • IDS Categories: {len(ids_rules)}")
    print(f"  • Monitoring Active: {monitor.monitoring_active}")
    print()
    print("Next Steps:")
    print("  1. Review firewall rules: firewall.get_all_rules()")
    print("  2. Monitor VPN status: vpn.get_tunnel_status()")
    print("  3. Check security alerts: ids.get_active_alerts()")
    print("  4. View compliance dashboard: monitor.get_monitoring_dashboard()")
    print()
    print("Documentation:")
    print("  • Integration Guide: docs/starlink_integration.md")
    print("  • Architecture: docs/architecture.md")
    print("  • Compliance: docs/compliance.md")
    print("=" * 60)

if __name__ == '__main__':
    main()
