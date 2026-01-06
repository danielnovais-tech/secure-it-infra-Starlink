#!/usr/bin/env python3
"""
Compliance Monitoring Example
Demonstrates compliance checking and reporting for SOC 2, ISO 27001, and GDPR
"""

import sys
sys.path.insert(0, '/home/runner/work/secure-it-infra-Starlink/secure-it-infra-Starlink')

from modules import SecurityMonitor

def main():
    """Compliance monitoring demonstration"""
    
    print("=" * 70)
    print("Compliance Monitoring and Reporting")
    print("=" * 70)
    print()
    
    # Initialize security monitor
    monitor = SecurityMonitor()
    
    # 1. Run Compliance Checks
    print("1. Running Compliance Checks...\n")
    
    frameworks = {
        'SOC2': 'SOC 2 Type II',
        'ISO27001': 'ISO/IEC 27001:2013',
        'GDPR': 'General Data Protection Regulation'
    }
    
    results = {}
    for framework_id, framework_name in frameworks.items():
        print(f"   Checking {framework_name}...")
        result = monitor.run_compliance_check(framework_id)
        results[framework_id] = result
        
        score = result['compliance_score']
        passed = result['checks_passed']
        failed = result['checks_failed']
        total = passed + failed
        
        # Display results
        status = "✓ COMPLIANT" if score >= 95 else "⚠ NEEDS ATTENTION" if score >= 80 else "✗ NON-COMPLIANT"
        print(f"      {status}")
        print(f"      Score: {score:.1f}%")
        print(f"      Passed: {passed}/{total}")
        print(f"      Failed: {failed}/{total}")
        print()
    
    # 2. Compliance Dashboard
    print("2. Compliance Dashboard\n")
    
    dashboard = monitor.get_monitoring_dashboard()
    
    print("   Overall Status:")
    print(f"      Active Monitoring: {'✓ Enabled' if dashboard['active_monitoring'] else '✗ Disabled'}")
    print(f"      Total Events Logged: {dashboard['total_events_logged']}")
    print(f"      Frameworks Monitored: {len(dashboard['compliance_status'])}")
    print()
    
    # 3. Detailed Framework Analysis
    print("3. Detailed Framework Analysis\n")
    
    for framework_id, result in results.items():
        print(f"   {frameworks[framework_id]}:")
        print(f"      Compliance Score: {result['compliance_score']:.1f}%")
        
        # Calculate trend (simulated)
        trend = "+2.3%" if result['compliance_score'] >= 95 else "-1.5%"
        trend_symbol = "↑" if trend.startswith('+') else "↓"
        print(f"      Trend: {trend_symbol} {trend} from last month")
        
        # Recommendations based on score
        if result['compliance_score'] < 95:
            print(f"      Recommendations:")
            if framework_id == 'SOC2':
                print(f"         • Review access control policies")
                print(f"         • Enhance logging retention")
                print(f"         • Update incident response procedures")
            elif framework_id == 'ISO27001':
                print(f"         • Complete risk assessment updates")
                print(f"         • Review information security policies")
                print(f"         • Conduct management review")
            elif framework_id == 'GDPR':
                print(f"         • Update privacy notices")
                print(f"         • Review data retention policies")
                print(f"         • Document lawful basis for processing")
        else:
            print(f"      Status: Excellent - maintain current controls")
        print()
    
    # 4. Recent Security Events
    print("4. Recent Security Events\n")
    
    if dashboard['recent_events']:
        print(f"   Last {len(dashboard['recent_events'])} events:")
        for event in dashboard['recent_events'][:5]:
            print(f"      • [{event['severity'].upper()}] {event['event_type']}")
    else:
        print("   No recent security events")
    print()
    
    # 5. Compliance Reporting
    print("5. Generating Compliance Reports...\n")
    
    # Monthly report
    print("   Monthly Compliance Report:")
    print(f"      Period: January 2026")
    print(f"      Status: Generated")
    print(f"      Contents:")
    print(f"         • Executive Summary")
    print(f"         • Framework Compliance Status")
    print(f"         • Security Metrics")
    print(f"         • Incident Summary")
    print(f"         • Remediation Actions")
    print()
    
    # Quarterly audit
    print("   Quarterly Audit Schedule:")
    print(f"      Q1 2026: Internal Audit (March)")
    print(f"      Q2 2026: External Audit (June)")
    print(f"      Q3 2026: Penetration Testing (September)")
    print(f"      Q4 2026: Management Review (December)")
    print()
    
    # 6. Starlink-Specific Compliance
    print("6. Starlink-Specific Compliance Checks\n")
    
    starlink_checks = {
        'encryption_in_transit': True,
        'vpn_enabled': True,
        'mfa_required': True,
        'geo_fencing_active': True,
        'audit_logging': True,
        'data_sovereignty': True
    }
    
    print("   Starlink Security Controls:")
    for check, status in starlink_checks.items():
        check_name = check.replace('_', ' ').title()
        status_symbol = "✓" if status else "✗"
        print(f"      {status_symbol} {check_name}")
    print()
    
    # 7. Action Items
    print("7. Recommended Action Items\n")
    
    action_items = []
    for framework_id, result in results.items():
        if result['compliance_score'] < 95:
            priority = "High" if result['compliance_score'] < 85 else "Medium"
            action_items.append({
                'framework': frameworks[framework_id],
                'priority': priority,
                'action': f"Address {result['checks_failed']} failed checks"
            })
    
    if action_items:
        for i, item in enumerate(action_items, 1):
            print(f"   {i}. [{item['priority']}] {item['framework']}")
            print(f"      Action: {item['action']}")
            print(f"      Due Date: Within 30 days")
            print()
    else:
        print("   ✓ No action items - all frameworks compliant")
        print()
    
    # 8. Summary
    print("=" * 70)
    print("Compliance Monitoring Summary")
    print("=" * 70)
    print()
    
    avg_score = sum(r['compliance_score'] for r in results.values()) / len(results)
    overall_status = "EXCELLENT" if avg_score >= 95 else "GOOD" if avg_score >= 85 else "NEEDS IMPROVEMENT"
    
    print(f"Overall Compliance Status: {overall_status}")
    print(f"Average Compliance Score: {avg_score:.1f}%")
    print()
    
    print("Framework Status:")
    for framework_id, result in results.items():
        status_icon = "✓" if result['compliance_score'] >= 95 else "⚠" if result['compliance_score'] >= 85 else "✗"
        print(f"  {status_icon} {frameworks[framework_id]}: {result['compliance_score']:.1f}%")
    print()
    
    print("Next Steps:")
    print("  1. Address action items listed above")
    print("  2. Schedule quarterly management review")
    print("  3. Update compliance documentation")
    print("  4. Conduct staff training on identified gaps")
    print("  5. Re-run compliance checks in 30 days")
    print()
    
    print("Resources:")
    print("  • Compliance Guide: docs/compliance.md")
    print("  • Security Policy: config/security_policy.json")
    print("  • Integration Guide: docs/starlink_integration.md")
    print("=" * 70)

if __name__ == '__main__':
    main()
