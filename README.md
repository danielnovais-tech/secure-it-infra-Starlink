# Secure IT Infrastructure - Starlink Enterprise Security Toolkit

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink connectivity in rural and remote areas.

## Overview

The **Secure IT Infrastructure - Starlink** toolkit provides comprehensive security auditing and monitoring capabilities for enterprises using Starlink connectivity. It helps ensure robust, scalable, and secure IT operations in environments where traditional connectivity options are limited.

## Features

- **Network Security Auditing**: Comprehensive checks for firewall status, open ports, DNS security, and network segmentation
- **Service Security Analysis**: Identifies unnecessary services, outdated software, and insecure service configurations
- **Encryption Validation**: Verifies TLS/SSL configurations, encrypted storage, and VPN encryption standards
- **VPN Configuration Assessment**: Validates VPN service status, authentication methods, and connectivity
- **Automated Reporting**: Generates detailed JSON reports with security scores and actionable recommendations

## Installation

### Prerequisites

- Python 3.7 or higher
- Linux-based operating system (Ubuntu, Debian, CentOS, etc.)
- Appropriate system permissions (some checks require sudo access)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

2. Make the script executable:
```bash
chmod +x secure_it_infra.py
```

3. (Optional) Create a custom configuration file:
```bash
cp config.example.json config.json
# Edit config.json with your specific settings
```

## Usage

### Basic Usage

Run a comprehensive security audit with default settings:
```bash
./secure_it_infra.py
```

Run with verbose output:
```bash
./secure_it_infra.py -v
```

### Comprehensive Audit

Run a full audit with a custom configuration and save the report:
```bash
./secure_it_infra.py --audit --config config.json --output security_report.json
```

Generate recommendations along with the audit:
```bash
./secure_it_infra.py --audit --recommendations
```

### Individual Security Checks

Check network security only:
```bash
./secure_it_infra.py --check-network
```

Check service security:
```bash
./secure_it_infra.py --check-services
```

Check encryption status:
```bash
./secure_it_infra.py --check-encryption
```

Validate VPN configuration:
```bash
./secure_it_infra.py --check-vpn
```

### Command-Line Options

```
Options:
  --audit                Run comprehensive security audit
  --check-network        Check network security only
  --check-services       Check services security only
  --check-encryption     Check encryption status only
  --check-vpn           Validate VPN configuration only
  -c, --config FILE     Path to configuration file
  -o, --output FILE     Path to save audit report
  --recommendations     Generate security recommendations
  -v, --verbose         Enable verbose output
  -h, --help           Show help message
```

## Configuration

The tool can be customized using a JSON configuration file. See `config.example.json` for a template.

### Configuration Options

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

- **starlink_gateway**: IP address of your Starlink gateway
- **critical_ports**: List of ports to check for security vulnerabilities
- **internal_subnets**: Private IP ranges used in your network
- **security_checks**: Enable/disable specific security check modules

## Security Checks

### Network Security
- Firewall status verification
- Open port scanning
- DNS security configuration
- Network segmentation validation

### Service Audit
- Identification of unnecessary/risky services
- Service version checking
- Service permission validation

### Encryption Check
- TLS/SSL configuration assessment
- Encrypted storage detection
- VPN encryption strength validation

### VPN Validation
- VPN service status
- Authentication method verification
- Connectivity testing

## Output and Reporting

The tool generates detailed reports in JSON format containing:
- Timestamp of the audit
- Results of each security check (passed, failed, warnings)
- Overall security score (0-100)
- Actionable recommendations

Example output structure:
```json
{
  "timestamp": "2026-01-06T23:00:00.000000",
  "checks": [
    {
      "name": "network_security",
      "passed": ["Firewall is active"],
      "failed": [],
      "warnings": ["Consider using secure DNS (DoH/DoT)"]
    }
  ],
  "overall_score": 85
}
```

## Logging

All audit activities are logged to `secure_it_infra.log` in the current directory. Logs include:
- Timestamp of each check
- Success/failure status
- Error messages and warnings
- Configuration loading status

## Use Cases

### Rural/Remote Enterprise Networks
Designed specifically for enterprises using Starlink in areas with limited traditional connectivity options.

### Security Compliance
Regular audits help maintain security compliance standards and identify vulnerabilities before they can be exploited.

### Infrastructure Monitoring
Continuous monitoring of security posture for Starlink-connected infrastructure.

### Remote Office Security
Validate security configurations for remote offices relying on Starlink connectivity.

## Best Practices

1. **Regular Audits**: Run comprehensive audits weekly or after any infrastructure changes
2. **Custom Configuration**: Tailor the configuration to your specific network environment
3. **Act on Recommendations**: Address failed checks and warnings promptly
4. **Monitor Trends**: Track security scores over time to identify degradation
5. **Combine with Other Tools**: Use alongside other security tools for comprehensive coverage

## Troubleshooting

### Permission Issues
Some checks require elevated privileges. Run with appropriate permissions:
```bash
sudo ./secure_it_infra.py --audit
```

### Service Detection
If services aren't being detected correctly, ensure:
- The system uses systemd for service management
- You have permissions to query service status

### Network Checks
For accurate network checks:
- Ensure the Starlink gateway IP is correctly configured
- Verify network connectivity before running audits

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

See the LICENSE file for details.

## Version

Current Version: 1.0.0

## Author

secure-it-infra Team

## Support

For issues and questions, please open an issue in the GitHub repository.
