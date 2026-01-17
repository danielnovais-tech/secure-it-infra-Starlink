#!/usr/bin/env python3
"""
Example: Comprehensive Security Scan
Demonstrates vulnerability scanning and configuration security assessment.
"""

from secure_it_starlink.scanning import VulnerabilityScanner, PortScanner
from secure_it_starlink.config import SecurityConfig, ConfigScanner


def main():
    print("=" * 70)
    print("Secure IT Starlink - Comprehensive Security Scan Example")
    print("=" * 70)
    print()

    # 1. Configuration Security Scan
    print("1. Configuration Security Assessment")
    print("-" * 70)
    
    # Use default secure configuration
    config = SecurityConfig()
    print("Scanning default security configuration...")
    validation = config.validate()
    
    print(f"Total checks: {validation['total_checks']}")
    print(f"Passed checks: {validation['passed_checks']}")
    print(f"Failed checks: {validation['failed_checks']}")
    
    if validation['failed_checks'] > 0:
        print("\nFindings:")
        for finding in validation['findings']:
            print(f"  [{finding['severity']}] {finding['message']}")
            if finding.get('recommendation'):
                print(f"    Recommendation: {finding['recommendation']}")
    else:
        print("\n✓ Configuration passed all security checks!")
    
    # 2. Test with insecure configuration
    print("\n2. Testing Insecure Configuration")
    print("-" * 70)
    
    insecure_config = {
        "encryption_enabled": False,
        "cipher_suite": "DES",
        "authentication": {
            "mfa_enabled": False,
            "min_password_length": 6
        },
        "allowed_protocols": ["SSLv3", "TLSv1.0"],
        "network": {
            "segmentation_enabled": False,
            "firewall_enabled": False
        },
        "username": "admin",
        "password": "admin"
    }
    
    vuln_scanner = VulnerabilityScanner()
    scan_result = vuln_scanner.scan_configuration(insecure_config)
    
    print(f"Vulnerabilities found: {scan_result['vulnerabilities_found']}")
    print("\nVulnerability Details:")
    for vuln in scan_result['vulnerabilities']:
        print(f"\n  [{vuln['severity']}] {vuln['description']}")
        print(f"    Location: {vuln.get('location', 'N/A')}")
        print(f"    Recommendation: {vuln['recommendation']}")
    
    # 3. Port Scanning
    print("\n3. Network Port Scanning")
    print("-" * 70)
    
    port_scanner = PortScanner()
    print("Scanning localhost for common ports...")
    
    common_ports = [22, 80, 443, 3306, 5432, 8080]
    scan = port_scanner.scan_ports("127.0.0.1", ports=common_ports, timeout=0.5)
    
    print(f"\nPorts scanned: {scan['ports_scanned']}")
    print(f"Open ports: {len(scan['open_ports'])}")
    
    if scan['open_ports']:
        print("\nOpen Ports:")
        for result in scan['scan_results']:
            if result['status'] == 'open':
                print(f"  Port {result['port']}: {result['service']} (OPEN)")
    else:
        print("\nNo open ports detected")
    
    # 4. Vulnerability Summary
    print("\n4. Overall Security Summary")
    print("-" * 70)
    
    vuln_summary = vuln_scanner.get_vulnerability_summary()
    print(f"Total scans performed: {vuln_summary['total_scans']}")
    print(f"Total vulnerabilities found: {vuln_summary['total_vulnerabilities']}")
    print("\nBy Severity:")
    for severity, count in vuln_summary['by_severity'].items():
        if count > 0:
            print(f"  {severity}: {count}")
    
    # 5. Recommendations
    print("\n5. Security Recommendations")
    print("-" * 70)
    print("✓ Enable encryption for all data transmission")
    print("✓ Use strong cipher suites (AES-256-GCM or better)")
    print("✓ Enable multi-factor authentication")
    print("✓ Use secure protocols (TLSv1.2, TLSv1.3)")
    print("✓ Enable network segmentation and firewall")
    print("✓ Change default credentials immediately")
    print("✓ Close unnecessary open ports")
    print("✓ Regularly scan for vulnerabilities")
    
    print("\n" + "=" * 70)
    print("Security scan completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
