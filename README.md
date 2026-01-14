# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Starlink Enterprise Security Audit Tool

A comprehensive security auditing tool designed specifically for enterprise infrastructures connected to Starlink satellite internet. This tool performs automated security checks across network configuration, services, encryption, and VPN setups.

## Features

- **Network Security Checks**: Validates firewall configuration, scans for open critical ports, checks DNS security, and evaluates network segmentation
- **Service Audit**: Identifies unnecessary services, checks for outdated software versions, and validates service permissions
- **Encryption Validation**: Verifies TLS/SSL configuration, checks for encrypted storage, and validates VPN encryption
- **VPN Configuration**: Tests VPN service status, authentication methods, and connectivity
- **Comprehensive Reporting**: Generates detailed JSON reports with security scores and actionable recommendations

## Installation

No external dependencies are required. The tool uses only Python 3 standard library modules.

```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
chmod +x starlink_security_auditor.py
```

## Usage

### Run a comprehensive security audit

```bash
python3 starlink_security_auditor.py --audit
```

### Run a comprehensive audit with custom configuration

```bash
python3 starlink_security_auditor.py --audit --config config.json
```

### Save audit report to file

```bash
python3 starlink_security_auditor.py --audit --output security_report.json
```

### Generate security recommendations

```bash
python3 starlink_security_auditor.py --audit --recommendations
```

### Run specific security checks

```bash
# Network security only
python3 starlink_security_auditor.py --check-network

# Services security only
python3 starlink_security_auditor.py --check-services

# Encryption status only
python3 starlink_security_auditor.py --check-encryption

# VPN configuration only
python3 starlink_security_auditor.py --check-vpn
```

### Enable verbose output

```bash
python3 starlink_security_auditor.py --audit --verbose
```

## Configuration

Create a custom configuration file (JSON format) to customize the security checks:

```json
{
  "starlink_gateway": "192.168.100.1",
  "critical_ports": [22, 80, 443, 3389, 5900],
  "internal_subnets": [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16"
  ],
  "security_checks": {
    "network_security": true,
    "service_audit": true,
    "encryption_check": true,
    "vpn_validation": true
  }
}
```

See `config.example.json` for a complete example.

## Security Checks

### Network Security
- Firewall status (ufw/iptables)
- Open critical ports scanning
- DNS security configuration
- Network segmentation validation

### Service Audit
- Unnecessary service detection
- Service version checks
- Service permission validation

### Encryption Status
- TLS/SSL configuration
- Encrypted storage detection (LUKS)
- VPN encryption strength

### VPN Validation
- VPN service status (OpenVPN, WireGuard, StrongSwan, IPSec)
- Authentication method validation
- Connectivity testing

## Requirements

- Python 3.6 or higher
- Linux operating system (for full functionality)
- Root/sudo access (for some checks like firewall status)

## Permissions

Some security checks require elevated privileges to run properly:
- Firewall status checks require `sudo` access
- Service auditing may require root access for complete results

## Output

The tool generates a JSON report with the following structure:

```json
{
  "timestamp": "2026-01-14T23:40:00.000000",
  "checks": [
    {
      "name": "network_security",
      "passed": ["Firewall is active"],
      "failed": [],
      "warnings": ["Open ports detected: [22, 80]"]
    }
  ],
  "overall_score": 75
}
```

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
