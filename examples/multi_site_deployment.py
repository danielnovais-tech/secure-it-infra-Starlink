#!/usr/bin/env python3
"""
Multi-Site Deployment Example
Demonstrates setting up secure infrastructure for multiple rural sites with Starlink
"""

import sys
import os
from modules import (
    FirewallRuleManager,
    VPNManager,
    RBACManager,
    SecurityMonitor
)

# Add the repository root to the path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

def main():
    """Multi-site deployment demonstration"""
    
    print("=" * 70)
    print("Multi-Site Rural Deployment with Starlink")
    print("=" * 70)
    print()
    
    # Define remote sites
    sites = [
        {
            'site_id': 'rural_clinic_1',
            'name': 'Rural Healthcare Clinic - North',
            'subnet': '10.1.0.0/24',
            'starlink_ip': '203.0.113.10',
            'location': 'Northern Territory',
            'type': 'healthcare'
        },
        {
            'site_id': 'mining_site_1',
            'name': 'Mining Operations - West',
            'subnet': '10.2.0.0/24',
            'starlink_ip': '203.0.113.20',
            'location': 'Western Region',
            'type': 'industrial'
        },
        {
            'site_id': 'research_station_1',
            'name': 'Agricultural Research Station',
            'subnet': '10.3.0.0/24',
            'starlink_ip': '203.0.113.30',
            'location': 'Central Plains',
            'type': 'research'
        }
    ]
    
    print(f"Deploying infrastructure for {len(sites)} remote sites\n")
    
    # 1. Configure VPN Hub-and-Spoke
    print("1. Configuring Hub-and-Spoke VPN Architecture...")
    vpn = VPNManager()
    
    # Configure multi-site mesh
    mesh_config = vpn.configure_multi_site(sites)
    print(f"   ✓ VPN topology: {mesh_config['topology']}")
    print(f"   ✓ Failover: {mesh_config['failover']}")
    print(f"   ✓ Routing: {mesh_config['routing']}")
    print()
    
    # Create tunnels for each site
    print("2. Creating VPN Tunnels...")
    tunnels = []
    for site in sites:
        tunnel = vpn.create_tunnel(
            endpoint=site['starlink_ip'],
            subnet=site['subnet'],
            bandwidth_limit='100Mbps'
        )
        tunnels.append(tunnel)
        print(f"   ✓ {site['name']}")
        print(f"      Endpoint: {tunnel['endpoint']}")
        print(f"      Subnet: {tunnel['subnet']}")
        print(f"      Protocol: {tunnel['protocol']}")
        print(f"      Bandwidth Limit: {tunnel['bandwidth_limit']}")
        print()
    
    # 3. Optimize for Starlink
    print("3. Applying Starlink Optimizations...")
    starlink_opt = vpn.optimize_for_starlink()
    print(f"   ✓ MTU: {starlink_opt['mtu']} bytes")
    print(f"   ✓ Keepalive: {starlink_opt['keepalive']} seconds")
    print(f"   ✓ QoS Enabled: {starlink_opt['qos_enabled']}")
    print(f"   ✓ Priority Traffic: {', '.join(starlink_opt['priority_traffic'])}")
    print()
    
    # 4. Configure Site-Specific Firewall Rules
    print("4. Configuring Site-Specific Security...")
    firewall = FirewallRuleManager()
    
    for site in sites:
        print(f"   {site['name']}:")
        
        # Base Starlink rules
        starlink_rules = firewall.configure_starlink_access()
        print(f"      ✓ Starlink access rules: {len(starlink_rules)}")
        
        # Site-specific rules based on type
        if site['type'] == 'healthcare':
            # HIPAA compliance rules
            firewall.add_rule(
                rule_type='inbound',
                source='telehealth_network',
                destination=site['subnet'],
                port=443,
                action='allow'
            )
            print("      ✓ Healthcare-specific rules (HIPAA compliance)")
            
        elif site['type'] == 'industrial':
            # OT/ICS security
            firewall.add_rule(
                rule_type='inbound',
                source='scada_network',
                destination=site['subnet'],
                port=502,  # Modbus
                action='allow'
            )
            print("      ✓ Industrial control system rules")
            
        elif site['type'] == 'research':
            # Research data transfer
            firewall.add_rule(
                rule_type='outbound',
                source=site['subnet'],
                destination='university_network',
                port=22,  # SSH
                action='allow'
            )
            print("      ✓ Research collaboration rules")
        print()
    
    # 5. Configure Role-Based Access Control
    print("5. Configuring Multi-Site Access Control...")
    rbac = RBACManager()
    
    # Configure site-specific access policies
    policy = rbac.configure_starlink_access_policy()
    print(f"   ✓ VPN Required: {policy['require_vpn']}")
    print(f"   ✓ MFA Required: {policy['require_mfa']}")
    print(f"   ✓ Session Timeout: {policy['session_timeout']}s")
    print(f"   ✓ IP Whitelisting: {policy['ip_whitelisting']}")
    print()
    
    # Assign site administrators
    site_admins = [
        ('admin_001', 'clinic_admin', 'rural_clinic_1'),
        ('admin_002', 'mining_admin', 'mining_site_1'),
        ('admin_003', 'research_admin', 'research_station_1')
    ]
    
    print("   Site Administrators:")
    for user_id, username, site_id in site_admins:
        rbac.assign_role(user_id, 'network_engineer')
        site = next(s for s in sites if s['site_id'] == site_id)
        print(f"      ✓ {username} assigned to {site['name']}")
    print()
    
    # 6. Configure Centralized Monitoring
    print("6. Configuring Centralized Monitoring...")
    monitor = SecurityMonitor()
    
    # Setup continuous monitoring for all sites
    monitoring = monitor.setup_continuous_monitoring()
    print(f"   ✓ Monitoring Scope: {len(monitoring['monitoring_scope'])} areas")
    print(f"   ✓ Alert Channels: {', '.join(monitoring['alerting']['channels'])}")
    print(f"   ✓ Auto-Remediation: {monitoring['automation']['auto_remediation']}")
    print()
    
    # Configure SIEM for all sites
    siem = monitor.configure_siem_integration()
    print("   Log Sources:")
    for source in siem['log_sources']:
        print(f"      • {source}")
    print(f"   ✓ Retention: {siem['retention_period_days']} days")
    print(f"   ✓ Real-time Correlation: {siem['real_time_correlation']}")
    print()
    
    # 7. Configure Incident Response
    print("7. Configuring Incident Response...")
    ir_config = monitor.configure_incident_response()
    
    print(f"   Playbooks: {len(ir_config['playbooks'])}")
    for playbook in ir_config['playbooks']:
        print(f"      • {playbook}")
    print()
    
    print("   Response SLAs:")
    for severity, sla in ir_config['response_time_sla'].items():
        print(f"      • {severity.capitalize()}: {sla}")
    print()
    
    # 8. Deployment Summary
    print("=" * 70)
    print("Multi-Site Deployment Complete!")
    print("=" * 70)
    print()
    print("Deployment Summary:")
    print(f"  • Total Sites: {len(sites)}")
    print(f"  • VPN Tunnels: {len(tunnels)}")
    print(f"  • Firewall Rules: {len(firewall.get_all_rules())}")
    print(f"  • Site Administrators: {len(site_admins)}")
    print(f"  • Monitoring: Active ({len(monitoring['monitoring_scope'])} areas)")
    print()
    
    print("Site Details:")
    for site in sites:
        print(f"\n  {site['name']}:")
        print(f"    Location: {site['location']}")
        print(f"    Type: {site['type']}")
        print(f"    Subnet: {site['subnet']}")
        print(f"    Starlink IP: {site['starlink_ip']}")
        print("    VPN Status: Connected")
        print("    Security: Configured")
    print()
    
    print("Next Steps:")
    print("  1. Test connectivity to all sites")
    print("  2. Verify VPN tunnels: vpn.get_tunnel_status()")
    print("  3. Monitor site health via dashboard")
    print("  4. Conduct security drills at each site")
    print("  5. Train site administrators")
    print()
    
    print("Documentation:")
    print("  • Integration Guide: docs/starlink_integration.md")
    print("  • Architecture Patterns: docs/architecture.md")
    print("=" * 70)

if __name__ == '__main__':
    main()
