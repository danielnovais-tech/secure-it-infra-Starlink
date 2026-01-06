# Starlink Security Auditor

A comprehensive security auditing tool designed specifically for Starlink-based enterprise infrastructures in remote and rural environments.

## Overview

The Starlink Security Auditor is an enterprise-ready security assessment tool that performs comprehensive security checks across multiple domains, with special considerations for connectivity-resilient security in Starlink deployments.

## Key Features

### 1. Comprehensive Security Auditing

- **Network Security Checks**: Firewall status, open ports, network configuration
- **Service Vulnerability Assessments**: SSH configuration, running services, service hardening
- **Encryption Status Verification**: Disk encryption (LUKS), SSL/TLS certificates
- **VPN Configuration Validation**: OpenVPN and WireGuard support, service status checks

### 2. Starlink-Specific Considerations

- Designed for **remote/rural enterprise environments**
- Focus on **connectivity-resilient security**
- **VPN validation** for secure remote access
- Optimized for high-latency, satellite-based connections

### 3. Enterprise-Ready Features

- **JSON Configuration Support**: Flexible, customizable audit scope
- **Detailed Logging**: Comprehensive logging to file and console
- **Comprehensive Reporting**: JSON and human-readable reports
- **Actionable Security Recommendations**: Clear guidance for remediation

### 4. Modular Design

- Each security domain is **independently testable**
- **Extensible architecture** for additional checks
- **Configurable audit scope** - enable/disable specific checks

### 5. Security Best Practices

- **Defense-in-depth approach**: Multiple layers of security validation
- **Encryption validation**: Ensures data protection at rest and in transit
- **Principle of least privilege checks**: File permissions and sudo configuration
- **Network segmentation validation**: Interface and routing verification

## Installation

### Requirements

- Python 3.7+
- Linux-based operating system
- Root/sudo access for certain checks

### Setup

1. Clone the repository:
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

2. Make the script executable:
```bash
chmod +x starlink_security_auditor.py
```

3. (Optional) Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

## Usage

### Basic Usage

Run with default configuration:
```bash
sudo python3 starlink_security_auditor.py
```

### Advanced Usage

Use a custom configuration file:
```bash
sudo python3 starlink_security_auditor.py --config config.example.json
```

Specify custom output file:
```bash
sudo python3 starlink_security_auditor.py --output my_audit_report.json
```

Run in quiet mode (no console output):
```bash
sudo python3 starlink_security_auditor.py --quiet
```

### Command-Line Options

- `--config, -c`: Path to JSON configuration file
- `--output, -o`: Output file for audit report (overrides config)
- `--quiet, -q`: Suppress console output (only log to file)

## Configuration

Create a configuration file based on `config.example.json`:

```json
{
  "audit_scope": {
    "network_security": true,
    "service_vulnerabilities": true,
    "encryption_validation": true,
    "vpn_validation": true,
    "network_segmentation": true,
    "privilege_checks": true
  },
  "starlink_settings": {
    "remote_environment": true,
    "connectivity_resilient": true,
    "require_vpn": true
  },
  "logging": {
    "level": "INFO",
    "file": "security_audit.log",
    "console": true
  },
  "reporting": {
    "format": "json",
    "output_file": "security_audit_report.json"
  }
}
```

### Configuration Options

#### Audit Scope
- `network_security`: Enable network security checks
- `service_vulnerabilities`: Enable service vulnerability assessments
- `encryption_validation`: Enable encryption status verification
- `vpn_validation`: Enable VPN configuration validation
- `network_segmentation`: Enable network segmentation checks
- `privilege_checks`: Enable principle of least privilege checks

#### Starlink Settings
- `remote_environment`: Optimizations for remote deployments
- `connectivity_resilient`: Focus on connectivity-resilient security
- `require_vpn`: Enforce VPN requirement for security

#### Logging
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `file`: Log file path
- `console`: Enable console logging

#### Reporting
- `format`: Report format (currently JSON)
- `output_file`: Output file for audit report

## Security Checks

### Network Security
- Firewall status (UFW/iptables)
- Open port scanning
- Network interface configuration

### Service Vulnerabilities
- SSH configuration hardening
- Running services inventory
- Service-specific security checks

### Encryption Status
- Disk encryption (LUKS) detection
- SSL/TLS certificate verification
- Encryption at rest and in transit

### VPN Configuration
- VPN software detection (OpenVPN, WireGuard)
- VPN service status
- Critical for Starlink remote access security

### Network Segmentation
- Network interface enumeration
- Routing table verification
- VLAN configuration validation

### Privilege Settings
- Sudo configuration review
- Sensitive file permissions
- Least privilege enforcement

## Output

### Console Output

The tool provides a human-readable summary:

```
================================================================================
STARLINK SECURITY AUDIT REPORT
================================================================================
Timestamp: 2026-01-06T23:15:00.000000
Hostname: starlink-gateway-01

Summary:
  Total Checks: 12
  Passed: 8
  Failed: 2
  Warnings: 2
  Info: 0

--------------------------------------------------------------------------------
Detailed Results:
--------------------------------------------------------------------------------

[✓] Firewall Status - PASS
    UFW firewall is active

[✗] VPN Software - FAIL
    No VPN software detected
    Recommendation: Install VPN software (OpenVPN or WireGuard)...
```

### JSON Report

Detailed machine-readable report in JSON format:

```json
{
  "timestamp": "2026-01-06T23:15:00.000000",
  "hostname": "starlink-gateway-01",
  "audit_results": [
    {
      "check_name": "Firewall Status",
      "status": "PASS",
      "message": "UFW firewall is active",
      "details": {...},
      "recommendation": null
    }
  ],
  "summary": {
    "PASS": 8,
    "FAIL": 2,
    "WARN": 2,
    "INFO": 0,
    "total": 12
  }
}
```

## Exit Codes

- `0`: Success (all checks passed)
- `1`: Failure (one or more checks failed)
- `2`: Warning (warnings present but no failures)

## Best Practices for Starlink Deployments

1. **Always enable VPN**: Critical for secure remote access over Starlink
2. **Monitor firewall rules**: Ensure only necessary ports are open
3. **Regular audits**: Run security audits regularly (weekly recommended)
4. **Review logs**: Check audit logs for security trends
5. **Act on recommendations**: Address FAIL and WARN results promptly

## Architecture

### Modular Design

```
SecurityAuditor
├── Network Security Module
├── Service Vulnerability Module
├── Encryption Validation Module
├── VPN Configuration Module
├── Network Segmentation Module
└── Privilege Checks Module
```

Each module is:
- Independently executable
- Easily testable
- Extensible for additional checks

### Extensibility

To add new security checks:

1. Create a new method in the `SecurityAuditor` class:
```python
def check_custom_security(self) -> None:
    """Custom security check."""
    self.logger.info("Running custom security checks...")
    # Perform checks
    self._add_result('Check Name', 'PASS/FAIL/WARN/INFO', 'Message', {...}, 'Recommendation')
```

2. Add to configuration:
```json
{
  "audit_scope": {
    "custom_security": true
  }
}
```

3. Call in `run_audit()` method:
```python
if scope.get('custom_security', False):
    self.check_custom_security()
```

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- New checks are modular and documented
- Configuration options are added for new features
- Security recommendations are actionable

## License

See LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Changelog

### Version 1.0.0
- Initial release with comprehensive security auditing
- Starlink-specific optimizations
- Modular architecture
- JSON configuration support
- Detailed logging and reporting
