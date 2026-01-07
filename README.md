# Secure IT Starlink

A comprehensive security tool foundation for Starlink-connected enterprise infrastructures.

## Overview

This toolkit provides essential security components for managing and securing enterprise infrastructures that rely on Starlink satellite connectivity. It includes modules for network monitoring, encryption, security logging, vulnerability scanning, access control, and configuration security.

## Features

### 🔒 Core Security Modules

1. **Network Security Monitoring** (`secure_it_starlink.network`)
   - Real-time network connection monitoring
   - Connection health checks and validation
   - Bandwidth and latency tracking
   - Authorized network validation

2. **Encryption & Key Management** (`secure_it_starlink.crypto`)
   - Strong encryption using industry-standard algorithms
   - Cryptographic key lifecycle management
   - Key generation, rotation, and revocation
   - Password-based key derivation (PBKDF2)

3. **Security Logging & Alerting** (`secure_it_starlink.logging`)
   - Comprehensive security event logging
   - Multi-level alert management (LOW, MEDIUM, HIGH, CRITICAL)
   - Alert tracking and resolution workflow
   - Structured logging with context

4. **Vulnerability Scanning** (`secure_it_starlink.scanning`)
   - Configuration vulnerability scanning
   - Port scanning and service discovery
   - Known vulnerability detection
   - Security assessment reports

5. **Access Control & Authentication** (`secure_it_starlink.access`)
   - Role-based access control (RBAC)
   - User authentication and session management
   - Access policy management
   - Audit logging for access events

6. **Configuration Security** (`secure_it_starlink.config`)
   - Security configuration validation
   - Default secure configuration templates
   - Configuration compliance checking
   - Configuration change tracking

## Installation

### Using pip

# Starlink Security Infrastructure

A comprehensive security solution for managed enterprise infrastructures supporting Starlink satellite connectivity. This package provides specialized adaptations for remote, unmanned locations with intermittent satellite connectivity.

## Features

### 🌐 Latency-Aware Security Policies
Automatically adjusts security measures based on real-time connection quality:
- Dynamic policy adaptation based on latency and packet loss
- Five security levels: Maximum, High, Medium, Low, and Emergency
- Intelligent feature toggling to maintain operations during degraded connectivity
- Bandwidth-aware security operations

### 🔄 Connection Resilience
Built-in failover mechanisms designed for satellite connectivity:
- Automatic reconnection with configurable retry logic
- Priority-based backup connection management (cellular, secondary satellite, etc.)
- Connection state monitoring and event tracking
- Uptime calculation and reporting
- Queue mode for offline operation

### 🛰️ Remote Management
Designed for unmanned remote locations with limited physical access:
- Autonomous, supervised, and manual operation modes
- Intelligent alert management with auto-resolution
- Remote command queuing and execution
- Health monitoring with trend analysis
- Periodic check-ins with minimal bandwidth overhead
- Configuration caching for offline operation

### 📊 Bandwidth Optimization
Security operations optimized for satellite bandwidth constraints:
- Configurable compression levels (none to maximum)
- Intelligent response caching with TTL
- Deferred operation queuing based on priority
- Bandwidth budget allocation across security functions
- Metrics tracking and optimization reporting
- Smart log transmission based on priority

## Installation

```bash
pip install starlink-security
```

For development:

```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from starlink_security import (
    ConnectionMonitor,
    LatencyAwarePolicyManager,
    ConnectionResilience,
    RemoteManager,
    BandwidthOptimizer
)

# Initialize components
monitor = ConnectionMonitor(check_interval=30)
policy_manager = LatencyAwarePolicyManager()

# Measure connection and adapt policy
metrics = monitor.measure_connection()
policy = policy_manager.update_policy(metrics)

print(f"Connection Quality: {metrics.quality.value}")
print(f"Security Level: {policy.level.value}")
```

### Using Configuration Presets

```python
from starlink_security.config import (
    create_remote_location_config,
    create_high_security_config,
    create_bandwidth_constrained_config
)

# Load configuration optimized for remote locations
config = create_remote_location_config()

# Initialize with configuration
monitor = ConnectionMonitor(
    check_interval=config.connection_check_interval,
    latency_threshold_excellent=config.latency_threshold_excellent,
    latency_threshold_good=config.latency_threshold_good,
    latency_threshold_fair=config.latency_threshold_fair,
    latency_threshold_poor=config.latency_threshold_poor
)
```

### Connection Resilience with Failover

```python
from starlink_security import ConnectionResilience
from starlink_security.resilience import BackupConnection

resilience = ConnectionResilience(
    reconnect_attempts=5,
    reconnect_delay_seconds=10
)

# Add backup connections
cellular_backup = BackupConnection(
    name="cellular_4g",
    priority=1,
    connection_type="cellular",
    enabled=True,
    max_bandwidth_mbps=25.0,
    latency_ms=80.0
)
resilience.add_backup_connection(cellular_backup)

# Monitor connection state
print(f"State: {resilience.get_state().value}")
print(f"Uptime: {resilience.get_uptime_percentage():.2f}%")
```

### Remote Management

```python
from starlink_security import RemoteManager
from starlink_security.remote_manager import ManagementMode, AlertSeverity

manager = RemoteManager(
    mode=ManagementMode.AUTONOMOUS,
    checkin_interval_minutes=60,
    autonomous_recovery=True
)

# Add alerts
manager.add_alert(
    severity=AlertSeverity.WARNING,
    component="connection_monitor",
    message="Latency spike detected"
)

# Perform check-in
checkin_data = manager.perform_checkin()
print(f"Alerts: {checkin_data['alerts_count']}")
```

### Bandwidth Optimization

```python
from starlink_security import BandwidthOptimizer
from starlink_security.bandwidth_optimizer import CompressionLevel

optimizer = BandwidthOptimizer(
    bandwidth_limit_mbps=100.0,
    enable_compression=True,
    enable_caching=True
)

# Configure compression
optimizer.set_compression_level(CompressionLevel.HIGH)

# Cache responses
optimizer.cache_response("security_rules", rules_data, ttl_seconds=3600)

# Calculate bandwidth budget
budget = optimizer.calculate_bandwidth_budget(total_bandwidth_mbps=150.0)
print(f"Security Ops: {budget.security_ops_mbps:.2f} Mbps")
```

## Configuration Profiles

Three pre-configured profiles are available:

### Remote Location Configuration
Optimized for unmanned remote locations with autonomous operation:
- Autonomous management mode
- High compression (bandwidth conservation)
- Extended check-in intervals
- Aggressive reconnection attempts

### High Security Configuration
Maximum security for critical infrastructure:
- Supervised management mode
- Full packet inspection
- Maximum logging verbosity
- Frequent monitoring

### Bandwidth Constrained Configuration
For severely limited bandwidth scenarios:
- Maximum compression
- Minimal logging
- Deferred non-critical operations
- Extended intervals

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           Starlink Security Infrastructure          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ Connection       │─────▶│ Policy           │   │
│  │ Monitor          │      │ Manager          │   │
│  └──────────────────┘      └──────────────────┘   │
│         │                           │              │
│         │                           │              │
│  ┌──────▼──────────┐      ┌────────▼─────────┐   │
│  │ Connection      │      │ Bandwidth        │   │
│  │ Resilience      │      │ Optimizer        │   │
│  └─────────────────┘      └──────────────────┘   │
│         │                           │              │
│         └───────────┬───────────────┘              │
│                     │                              │
│              ┌──────▼──────────┐                   │
│              │ Remote          │                   │
│              │ Manager         │                   │
│              └─────────────────┘                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=starlink_security --cov-report=html
```

## Examples

See the `examples/` directory for comprehensive usage examples:

```bash
python examples/usage_examples.py
```

## Use Cases

- **Remote Oil & Gas Facilities**: Unmanned monitoring stations with Starlink connectivity
- **Maritime Operations**: Vessels with satellite connectivity requiring autonomous security
- **Remote Research Stations**: Arctic/Antarctic facilities with intermittent connectivity
- **Mobile Command Centers**: Temporary deployments with satellite backhaul
- **Rural Infrastructure**: Remote cell towers and edge computing nodes
- **Disaster Recovery**: Emergency response units with satellite communications

## Requirements

- Python 3.8 or higher
- No external dependencies for core functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issue tracker.
# Secure IT Starlink

Enterprise-grade security and monitoring solutions for managed Starlink infrastructures.

## Overview

Secure IT Starlink provides comprehensive security monitoring, automated threat response, and performance tracking for enterprise Starlink deployments. The system includes:

- **Comprehensive Metrics**: Security scoring, connection stability monitoring, and performance analysis
- **Automated Responses**: Threat containment, policy enforcement, and failover activation
- **Detailed Logging**: Structured JSON logging with event correlation
- **Configuration Management**: YAML-based configuration with deep merging support

## Features

### 1. Comprehensive Metrics

The metrics system provides real-time monitoring across three key areas:

#### Security Scoring
- Firewall status monitoring
- Encryption level assessment
- Authentication strength validation
- Vulnerability tracking
- Patch level monitoring

#### Connection Stability
- Uptime percentage tracking
- Packet loss monitoring
- Latency measurement
- Jitter analysis
- Signal strength monitoring

#### Performance Monitoring
- Throughput analysis
- Bandwidth utilization tracking
- CPU usage monitoring
- Memory usage tracking
- Disk I/O monitoring

Each metric category has configurable weights and thresholds to calculate composite scores.

### 2. Automated Responses

The automated response system provides intelligent threat mitigation:

#### Threat Containment
- Device isolation for compromised endpoints
- IP address blocking for malicious sources
- Traffic quarantine for suspicious patterns
- Configurable severity thresholds
- Cooldown periods to prevent action loops

#### Policy Enforcement
- Bandwidth limit enforcement
- Unauthorized access blocking
- Malware detection and isolation
- Automatic policy violation handling

#### Failover Activation
- Automatic backup link switching on connection loss
- Load balancing on performance degradation
- Emergency shutdown on security breaches
- Priority-based backup link selection

### 3. Detailed Logging

Advanced logging capabilities with:

#### Structured Logging
- JSON-formatted log entries
- Configurable log levels per component
- Multiple output destinations (file, console, syslog)
- Automatic log rotation
- Hostname and process ID tracking

#### Event Correlation
- Pattern detection across multiple events
- Brute force attack detection
- Data exfiltration pattern recognition
- Configurable correlation windows
- Incident aggregation and reporting

### 4. Configuration Management

Flexible YAML-based configuration system:

- Deep merging of configuration files
- Environment-specific overrides
- Dot-notation access to nested values
- Runtime configuration updates
- Configuration validation
# Secure IT Infrastructure - Starlink
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
chmod +x starlink_security_auditor.py
```

3. (Optional) Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
chmod +x secure_it_infra.py
```

3. (Optional) Create a custom configuration file:
```bash
cp config.example.json config.json
# Edit config.json with your specific settings
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
STARLINK SECURITY AUDIT REPORT
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
# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Components

### Incident Response System
A YAML-based automated incident response handler for high-severity security events such as malware detection and security breaches.

**Features:**
- YAML-configured incident definitions
- Automated response actions: isolation, scanning, notifications, logging
- Priority-based execution
- Multi-channel alerting (email, SMS, Slack, PagerDuty)
- SIEM integration
- Forensic analysis capabilities

**Quick Start:**
```bash
cd incident_response
pip install -r requirements.txt
python handler.py
```

See [incident_response/README.md](incident_response/README.md) for detailed documentation.
## Features

### Threat Detection System (YAML-based)

A comprehensive threat detection system that provides:

- **Anomaly Detection**: Scans for anomalies in network traffic and system behavior
  - Failed login monitoring
  - Connection rate analysis
  - Bandwidth usage tracking
  - Port scan detection

- **Brute-force Attack Detection**: Analyzes logs for attack patterns
  - SSH brute-force attempts
  - HTTP authentication attacks
  - FTP login attacks
  - Configurable pattern matching with regex

- **Threat Intelligence Integration**: Updates from external threat feeds
  - DShield.org recommended block list
  - Emerging Threats compromised IPs
  - Automatic periodic updates
  - IP reputation checking

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Update threat intelligence feeds
python threat_detection/threat_detection.py --update-feeds

# Analyze a log file for brute-force attempts
python threat_detection/threat_detection.py --analyze-log /var/log/auth.log

# Monitor log files continuously
python threat_detection/threat_detection.py --monitor /var/log/auth.log /var/log/syslog

# Run example demonstrations
python examples.py
## Network Monitoring System

A comprehensive YAML-based network monitoring solution that tracks critical network metrics and security parameters for Starlink infrastructure.

### Features

- **Latency Monitoring**: Measures network latency (min/max/avg) using ICMP ping
- **Jitter Tracking**: Monitors variation in latency to detect network instability
- **Packet Loss Detection**: Tracks packet loss percentages to identify network issues
- **Throughput Measurement**: Measures network throughput for performance analysis
- **Device Connection Tracking**: Detects active devices on the network
- **Unauthorized Device Detection**: Identifies unauthorized devices by comparing against a whitelist
- **Open Port Scanning**: Scans critical systems for open ports to identify potential security vulnerabilities

### Installation

1. Clone this repository:
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

2. Install dependencies:
## Usage Examples

```bash
# Run as a daemon (production)
python starlink_security.py --daemon --config /path/to/config.yaml

# Generate security report
python starlink_security.py --report

# Check current status
python starlink_security.py --status

# Interactive mode with logging
python starlink_security.py --config ./security_config.yaml
```
## Overview

This repository provides a comprehensive security framework for Starlink infrastructure management, including six core security modules:

### Security Modules

1. **Network Monitor** - Device discovery, port scanning, and anomaly detection
2. **Threat Detector** - Threat intelligence feeds, log analysis, and malware detection
3. **Policy Enforcer** - Dynamic policy application based on security level
4. **Incident Responder** - Automated response to security incidents
5. **VPN Manager** - Secure connectivity management
6. **Backup Manager** - Failover and redundancy management

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
pip install -r requirements.txt
pip install -e .
```

## Configuration

### Default Configuration

The default configuration is located at `configs/default_config.yaml`. This file contains all available settings with sensible defaults.

### Custom Configuration

Create your own configuration file to override defaults:

```yaml
# custom_config.yaml
metrics:
  collection:
    interval: 30  # Collect metrics every 30 seconds
  
  security:
    thresholds:
      critical: 95  # Adjust critical threshold

automated_responses:
  threat_containment:
    auto_execute: true  # Enable automatic execution

logging:
  structured:
    level: DEBUG  # Set debug logging
```

Load your custom configuration:

```bash
secure-it-starlink -c /path/to/custom_config.yaml
```

### Configuration Merging

The system supports deep merging of multiple configuration files. This allows you to:

1. Start with the default configuration
2. Layer environment-specific settings
3. Apply user-specific overrides

Example:

```python
from secure_it_starlink.config import ConfigurationManager

config = ConfigurationManager('configs/default_config.yaml')
config.load_and_merge('configs/production.yaml')
config.load_and_merge('configs/user_overrides.yaml')
```

## Usage

### Starting the Monitoring System

```bash
# Use default configuration
secure-it-starlink

# Use custom configuration
secure-it-starlink -c /path/to/config.yaml

# Check system status
secure-it-starlink --status
```

### Programmatic Usage

```python
from secure_it_starlink import (
    ConfigurationManager,
    MetricsCollector,
    AutomatedResponseCoordinator,
    StructuredLogger
)

# Initialize components
config = ConfigurationManager()
logger = StructuredLogger(config.get('logging'))
metrics = MetricsCollector(config.get('metrics'))
responses = AutomatedResponseCoordinator(config.get('automated_responses'))

# Collect metrics
metrics_data = metrics.collect_metrics(
    security_data={'firewall_status': 95, 'encryption_level': 90},
    connection_data={'uptime_percentage': 99.5, 'latency': 25},
    performance_data={'cpu_usage': 45, 'memory_usage': 60}
)

# Process security events
event = {
    'type': 'security_threat',
    'severity': 'high',
    'device_id': 'device-001',
    'source_ip': '192.168.1.100',
    'reason': 'Malware detected'
}
actions = responses.process_event(event)

# Log with correlation
logger.info("Security event processed", event_type='security_threat', **event)
```

### Metrics Collection Example

```python
from secure_it_starlink.metrics import MetricsCollector

# Initialize collector
collector = MetricsCollector({
    'security': {'weight': 0.4},
    'connection': {'weight': 0.3},
    'performance': {'weight': 0.3}
})

# Collect and display metrics
metrics = collector.collect_metrics(
    security_data={
        'firewall_status': 95.0,
        'encryption_level': 90.0,
        'authentication_strength': 85.0
    },
    connection_data={
        'uptime_percentage': 99.8,
        'packet_loss': 0.1,
        'latency': 25.0
    },
    performance_data={
        'throughput_score': 85.0,
        'cpu_usage': 45.0,
        'memory_usage': 60.0
    }
)

print(f"Composite Score: {metrics['composite_score']:.2f}")
print(f"Security Level: {metrics['security']['level']}")
print(f"Connection Level: {metrics['connection']['level']}")
print(f"Performance Level: {metrics['performance']['level']}")
```

## Architecture

```
secure_it_starlink/
├── config/              # Configuration management
│   └── config_loader.py # YAML-based config with deep merging
├── metrics/             # Metrics collection and monitoring
│   └── collector.py     # Security, connection, and performance metrics
├── automated_responses/ # Automated threat response
│   └── coordinator.py   # Threat containment, policy, and failover
├── logging/            # Structured logging system
│   └── structured_logger.py # JSON logging with event correlation
├── utils/              # Utility functions
└── main.py            # Main application entry point
```

## Security Considerations

- **Least Privilege**: Run the application with minimal required permissions
- **Secure Configuration**: Store sensitive configuration values securely
- **Log Sanitization**: Ensure logs don't contain sensitive information
- **Access Control**: Restrict access to configuration and log files
- **Network Security**: Use encrypted connections for remote logging

## Logging

Logs are written to multiple destinations as configured:

- **File**: `/var/log/secure-it-starlink/app.log` (with rotation)
- **Console**: Real-time monitoring output
- **Syslog**: Optional remote logging

All logs are in structured JSON format for easy parsing and analysis.

## Monitoring and Alerts

The system provides multiple alert channels:

- Email notifications
- SMS alerts
- Webhook integration
- Log-based alerts

Configure alert channels in the configuration file under `application.alerts`.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

### Setup

1. Clone the repository:
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

2. (Optional) Install dependencies for enhanced functionality:
```bash
pip install -r requirements.txt
```

### Configuration

Edit `threat_detection/config/threat_rules.yaml` to customize:
- Detection thresholds
- Brute-force patterns
- Threat intelligence feeds
- Logging and alerts

## Documentation

See [threat_detection/README.md](threat_detection/README.md) for detailed documentation.

## Testing

```bash
# Run all tests
python threat_detection/tests/test_anomaly_detector.py
python threat_detection/tests/test_brute_force_detector.py
python threat_detection/tests/test_threat_intelligence.py
```

## License

See [LICENSE](LICENSE) file for details.
Create a YAML configuration file to define your monitoring targets and parameters. See `config.example.yaml` for a complete example.

Example configuration:
```yaml
monitoring:
  targets:
    - host: "8.8.8.8"
      monitor_latency: true
      monitor_jitter: true
      monitor_packet_loss: true
      ping_count: 4
      jitter_count: 10
      packet_loss_count: 20
      
    - host: "192.168.1.1"
      monitor_latency: true
      scan_ports: true
      ports_to_scan: [22, 80, 443]

  network:
    subnet: "192.168.1.0/24"
    detect_devices: true
    check_unauthorized: true
    authorized_devices:
      - "192.168.1.1"
      - "192.168.1.10"
```

### Usage

Run the network monitor with your configuration file:

```bash
python network_monitor.py config.example.yaml
```

Generate a report file:
```bash
python network_monitor.py config.example.yaml --output report.txt
```

Output results in JSON format:
```bash
python network_monitor.py config.example.yaml --json
```

Save JSON results to a file:
```bash
python network_monitor.py config.example.yaml --json --output results.json
```

### Testing

Run the test suite to verify the monitoring system:

```bash
python -m unittest test_network_monitor.py
```

Or run tests with verbose output:
```bash
python -m unittest test_network_monitor.py -v
```

### Configuration Options

#### Target Monitoring Options

- `host`: IP address or hostname to monitor (required)
- `monitor_latency`: Enable latency monitoring (default: true)
- `monitor_jitter`: Enable jitter monitoring (default: true)
- `monitor_packet_loss`: Enable packet loss monitoring (default: true)
- `monitor_throughput`: Enable throughput monitoring (default: false)
- `scan_ports`: Enable port scanning (default: false)
- `ports_to_scan`: List of ports to scan (required if scan_ports is true)
- `ping_count`: Number of pings for latency test (default: 4)
- `jitter_count`: Number of pings for jitter test (default: 10)
- `packet_loss_count`: Number of pings for packet loss test (default: 20)
- `throughput_port`: Port to use for throughput test (default: 80)

#### Network-Wide Options

- `subnet`: Network subnet in CIDR notation (e.g., "192.168.1.0/24")
- `detect_devices`: Enable device detection (default: false)
- `check_unauthorized`: Enable unauthorized device detection (default: false)
- `authorized_devices`: List of authorized IP addresses

### Output Format

The monitoring system generates a comprehensive report including:

1. **Latency Report**: Min, max, and average latency for each target
2. **Jitter Report**: Jitter statistics including average, max, min, and standard deviation
3. **Packet Loss Report**: Percentage of packets lost per target
4. **Throughput Report**: Measured throughput in Mbps
5. **Open Ports Report**: List of open ports detected on critical systems
6. **Unauthorized Devices Report**: Warning alerts for any unauthorized devices detected
7. **Device Connections Report**: List of all active devices on the network

### Security Considerations

- **Port Scanning**: Use port scanning responsibly and only on systems you own or have permission to scan
- **Network Scanning**: Device detection performs network scans which may be detected by intrusion detection systems
- **Authorized Devices**: Keep the authorized devices list up-to-date to ensure accurate unauthorized device detection
- **Permissions**: Some monitoring features may require elevated privileges (e.g., raw socket access for ICMP)

### Requirements

- Python 3.6 or higher
- PyYAML 6.0 or higher
- Network connectivity to target systems
- Appropriate permissions for network operations (ICMP, port scanning)

### License

This project is licensed under the MIT License - see the LICENSE file for details.
### For development

```bash
pip install -r requirements-dev.txt
```

## Quick Start

### Network Monitoring

```python
from secure_it_starlink.network import NetworkMonitor

# Initialize network monitor
monitor = NetworkMonitor()

# Start monitoring
monitor.start_monitoring()

# Check connection health
health = monitor.check_connection_health("8.8.8.8")
print(f"Connection status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")

# Get statistics
stats = monitor.get_connection_stats()
print(f"Health ratio: {stats['health_ratio']}")
```

### Encryption

```python
from secure_it_starlink.crypto import EncryptionManager

# Initialize encryption manager
encryptor = EncryptionManager()

# Encrypt sensitive data
plaintext = "Sensitive infrastructure data"
encrypted = encryptor.encrypt(plaintext)
print(f"Encrypted: {encrypted}")

# Decrypt data
decrypted = encryptor.decrypt(encrypted)
print(f"Decrypted: {decrypted}")

# Rotate encryption key
new_key = encryptor.rotate_key()
```

### Security Logging

```python
from secure_it_starlink.logging import SecurityLogger, AlertManager, AlertSeverity

# Initialize logger
logger = SecurityLogger(log_file="/var/log/security.log")

# Log security events
logger.info("User logged in", {"username": "admin", "ip": "192.168.1.100"})
logger.warning("Multiple failed login attempts", {"username": "test", "attempts": 3})
logger.critical("Unauthorized access attempt detected", {"resource": "admin_panel"})

# Create and manage alerts
alert_manager = AlertManager()
alert = alert_manager.create_alert(
    AlertSeverity.HIGH,
    "Suspicious Activity Detected",
    "Multiple failed authentication attempts from unknown IP"
)
```

### Vulnerability Scanning

```python
from secure_it_starlink.scanning import VulnerabilityScanner, PortScanner

# Scan configuration for vulnerabilities
scanner = VulnerabilityScanner()
config = {
    "encryption_enabled": False,
    "cipher_suite": "DES",
    "username": "admin",
    "password": "admin"
}
results = scanner.scan_configuration(config)
print(f"Vulnerabilities found: {results['vulnerabilities_found']}")

# Scan network ports
port_scanner = PortScanner()
scan_results = port_scanner.scan_ports("192.168.1.1", ports=[22, 80, 443, 3389])
print(f"Open ports: {scan_results['open_ports']}")
```

### Access Control

```python
from secure_it_starlink.access import AccessController, AuthenticationManager

# Set up access control
controller = AccessController()
controller.create_policy(
    "admin-policy",
    resource="admin_panel",
    allowed_actions=["read", "write", "delete"],
    principals=["admin", "super_user"]
)

# Check access
decision = controller.check_access("admin", "admin_panel", "read")
print(f"Access allowed: {decision['allowed']}")

# User authentication
auth_manager = AuthenticationManager()
auth_manager.create_user("admin", "SecureP@ssw0rd123", roles=["administrator"])
session_token = auth_manager.authenticate("admin", "SecureP@ssw0rd123")
```

### Configuration Security

```python
from secure_it_starlink.config import SecurityConfig, ConfigScanner

# Use default secure configuration
config = SecurityConfig()
print(config.get("encryption_enabled"))  # True
print(config.get("authentication.mfa_enabled"))  # True

# Customize configuration
config.set("authentication.session_timeout_minutes", 15)
config.update({
    "network.firewall_enabled": True,
    "logging.level": "DEBUG"
})

# Validate configuration
validation = config.validate()
print(f"Passed checks: {validation['passed_checks']}")
print(f"Failed checks: {validation['failed_checks']}")
```

## Configuration Examples

See the `examples/` directory for complete configuration examples:

- `examples/network_config.yaml` - Network security configuration
- `examples/security_config.yaml` - Full security configuration
- `examples/alert_rules.yaml` - Alert and notification rules

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=secure_it_starlink tests/
```

## Development

### Code Style

This project uses:
- Black for code formatting
- Flake8 for linting
- MyPy for type checking

```bash
# Format code
black secure_it_starlink/

# Lint
flake8 secure_it_starlink/

# Type check
mypy secure_it_starlink/
```

## Security Considerations

- **Always use strong encryption**: The toolkit defaults to AES-256-GCM
- **Rotate keys regularly**: Use the key rotation features for cryptographic keys
- **Enable MFA**: Multi-factor authentication should be enabled for all users
- **Monitor continuously**: Keep network monitoring active to detect anomalies
- **Review logs regularly**: Security logs should be reviewed for suspicious activity
- **Keep configurations secure**: Store configuration files with appropriate permissions

## Architecture

```
secure_it_starlink/
├── network/        # Network monitoring and validation
├── crypto/         # Encryption and key management
├── logging/        # Security logging and alerting
├── scanning/       # Vulnerability and port scanning
├── access/         # Access control and authentication
└── config/         # Configuration security and management
```

## Requirements

- Python 3.8+
- cryptography >= 41.0.0
- requests >= 2.31.0
- python-dateutil >= 2.8.0
- pyyaml >= 6.0

## License

MIT License - see LICENSE file for details
## Usage

### Running the Main Application

```bash
python main.py
```

This will initialize all security modules and demonstrate their capabilities.

### Running Examples

```bash
python examples.py
```

This demonstrates practical usage scenarios including incident response, VPN failover, backup strategies, and threat hunting.

### Using Individual Modules

#### Network Monitor

```python
from security_modules import NetworkMonitor

# Initialize the network monitor
monitor = NetworkMonitor(network_range="192.168.1.0/24")

# Discover devices
devices = monitor.discover_devices()

# Scan ports on a specific device
port_results = monitor.scan_ports("192.168.1.100", ports=[22, 80, 443])

# Detect anomalies
anomalies = monitor.detect_anomalies()

# Get network status
status = monitor.get_network_status()
```

#### Threat Detector

```python
from security_modules import ThreatDetector
from security_modules.threat_detector import ThreatLevel

# Initialize the threat detector
detector = ThreatDetector()

# Update threat intelligence feeds
detector.update_threat_feeds([
    "https://threat-feed-1.example.com",
    "https://threat-feed-2.example.com"
])

# Analyze logs
events = detector.analyze_logs("/var/log/syslog")

# Scan for malware
result = detector.detect_malware("/path/to/suspicious/file")

# Check IP reputation
reputation = detector.check_ip_reputation("192.168.1.50")

# Report a threat
threat_id = detector.report_threat(
    "brute_force",
    {"source": "192.168.1.50", "attempts": 100},
    ThreatLevel.HIGH
)
```

#### Policy Enforcer

```python
from security_modules import PolicyEnforcer
from security_modules.policy_enforcer import SecurityLevel

# Initialize the policy enforcer
enforcer = PolicyEnforcer(default_security_level=SecurityLevel.MEDIUM)

# Set security level
enforcer.set_security_level(SecurityLevel.HIGH)

# Enforce a policy
decision = enforcer.enforce_policy(
    resource="database",
    action="write",
    context={"user": "admin", "role": "administrator"}
)

# Add custom policy
enforcer.add_custom_policy(
    "require_vpn",
    {"condition": "source_network != vpn", "action": "deny"}
)
```

#### Incident Responder

```python
from security_modules import IncidentResponder
from security_modules.incident_responder import IncidentSeverity

# Initialize the incident responder
responder = IncidentResponder()

# Create an incident
incident_id = responder.create_incident(
    incident_type="malware",
    severity=IncidentSeverity.CRITICAL,
    description="Ransomware detected",
    affected_systems=["server-01", "server-02"]
)

# Add custom response playbook
responder.add_playbook(
    "data_breach",
    [
        "isolate_affected_systems",
        "notify_security_team",
        "preserve_evidence",
        "initiate_forensics"
    ]
)

# Resolve an incident
responder.resolve_incident(incident_id, "Malware removed, systems cleaned")
```

#### VPN Manager

```python
from security_modules import VPNManager
from security_modules.vpn_manager import VPNProtocol

# Initialize the VPN manager
vpn = VPNManager(default_protocol=VPNProtocol.WIREGUARD)

# Create VPN configuration
config_id = vpn.create_vpn_config(
    config_name="Office VPN",
    protocol=VPNProtocol.WIREGUARD,
    server="vpn.example.com",
    port=51820
)

# Connect to VPN
vpn.connect(config_id)

# Check connection status
status = vpn.check_connection_status(config_id)

# Enable failover
vpn.enable_failover(primary_config_id, backup_config_id)

# Disconnect
vpn.disconnect(config_id)
```

#### Backup Manager

```python
from security_modules import BackupManager
from security_modules.backup_manager import BackupType

# Initialize the backup manager
backup = BackupManager()

# Create a backup
backup_id = backup.create_backup(
    backup_name="Daily Backup",
    backup_type=BackupType.FULL,
    source_paths=["/data", "/config"],
    destination="/backups",
    encryption=True
)

# Verify backup
backup.verify_backup(backup_id)

# Restore backup
backup.restore_backup(backup_id, "/restore/path")

# Configure failover
failover_id = backup.configure_failover(
    service_name="Database",
    primary_endpoint="db-1.local",
    backup_endpoints=["db-2.local", "db-3.local"]
)

# Trigger manual failover
backup.trigger_failover(failover_id, reason="Primary server maintenance")

# Check redundancy
redundancy = backup.check_redundancy("database", required_replicas=3)
The **Secure IT Infrastructure for Starlink** provides a comprehensive core security foundation for managing enterprise infrastructures that use Starlink satellite connectivity. This package offers structured security management, connection type handling, event-driven architecture, and encryption capabilities.

## Features

### 🔒 Structured Security Levels

Four distinct security levels for granular control:

- **NORMAL**: Standard operational security level
- **ELEVATED**: Increased security monitoring and controls
- **CRITICAL**: Maximum security protocols activated
- **RECOVERY**: System recovery mode with restricted access

### 🌐 Connection Type Management

Support for different network connection modes:

- **STARLINK_ONLY**: Exclusive Starlink satellite connection
- **HYBRID**: Combined Starlink and terrestrial connection
- **FAILOVER**: Automatic failover between connection types

### 📡 Event-Driven Architecture

Robust event system with queued security events:

- Thread-safe event queue
- Multiple event types (security changes, connection status, intrusions, etc.)
- Event handlers with async support
- Event history with filtering capabilities

### 🔐 Encryption Management

Secure handling of sensitive data:

- Fernet symmetric encryption
- Password-based key derivation (PBKDF2HMAC)
- Key rotation support
- String and byte encryption

## Installation

```bash
pip install -e .
```

### Development Installation

```bash
pip install -r requirements-dev.txt
```

## Quick Start

```python
from secure_it_infra import (
    SecurityLevel,
    ConnectionType,
    SecurityEvent,
    SecurityEventQueue,
    EventType,
    EncryptionManager,
)

# Create a security event
event = SecurityEvent(
    event_type=EventType.SECURITY_LEVEL_CHANGE,
    security_level=SecurityLevel.ELEVATED,
    message="Security level elevated",
)

# Initialize event queue
queue = SecurityEventQueue()
queue.put(event)

# Encrypt sensitive data
manager = EncryptionManager.from_password("secure_password")
encrypted = manager.encrypt_str("sensitive data")
decrypted = manager.decrypt_str(encrypted)
```

## Usage Examples

### Security Levels

```python
from secure_it_infra import SecurityLevel

# Compare security levels
if SecurityLevel.CRITICAL.is_higher_than(SecurityLevel.ELEVATED):
    print("Critical security measures activated")

# Check priority
print(f"Priority: {SecurityLevel.RECOVERY.priority}")  # Output: 3
```

### Connection Types

```python
from secure_it_infra import ConnectionType

# Check connection capabilities
connection = ConnectionType.HYBRID
if connection.supports_redundancy:
    print("Redundancy available")

# Verify satellite-only mode
if ConnectionType.STARLINK_ONLY.is_satellite_only:
    print("Operating in satellite-only mode")
```

### Event Queue

```python
from secure_it_infra import SecurityEvent, SecurityEventQueue, EventType

# Create and manage events
queue = SecurityEventQueue()

event = SecurityEvent(
    event_type=EventType.INTRUSION_DETECTED,
    security_level=SecurityLevel.CRITICAL,
    source="firewall",
    message="Unauthorized access attempt",
    data={"ip": "192.168.1.100"},
)

queue.put(event)

# Process events
while not queue.is_empty():
    event = queue.get()
    print(f"Event: {event.message}")

# Filter event history
critical_events = queue.get_history(security_level=SecurityLevel.CRITICAL)
```

### Async Event Processing

```python
import asyncio
from secure_it_infra import SecurityEventQueue, EventType

async def main():
    queue = SecurityEventQueue()
    
    # Register event handler
    def handle_intrusion(event):
        print(f"⚠️  {event.message}")
    
    queue.register_handler(EventType.INTRUSION_DETECTED, handle_intrusion)
    
    # Start processing
    process_task = asyncio.create_task(queue.process_events())
    
    # Add events...
    # (events will be handled automatically)
    
    # Stop processing
    queue.stop_processing()
    await process_task

asyncio.run(main())
```

### Encryption

```python
from secure_it_infra import EncryptionManager

# Auto-generated key
manager = EncryptionManager()
encrypted = manager.encrypt_str("API Key: sk_live_123")
decrypted = manager.decrypt_str(encrypted)

# Password-based encryption
manager = EncryptionManager.from_password("my_password")
encrypted = manager.encrypt_str("secret data")

# Recreate manager with same password and salt
restored = EncryptionManager.from_password("my_password", salt=manager.salt)
decrypted = restored.decrypt_str(encrypted)

# Key rotation
old_key = manager.rotate_key()
```

## Running Examples

A comprehensive example demonstrating all features:

```bash
python examples/basic_usage.py
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=secure_it_infra --cov-report=html
```

## API Reference

### SecurityLevel

Enum with four security levels: `NORMAL`, `ELEVATED`, `CRITICAL`, `RECOVERY`

**Methods:**
- `is_higher_than(other)`: Compare security levels
- `is_lower_than(other)`: Compare security levels

**Properties:**
- `priority`: Numeric priority (0-3)

### ConnectionType

Enum with three connection types: `STARLINK_ONLY`, `HYBRID`, `FAILOVER`

**Properties:**
- `supports_redundancy`: Whether connection supports redundancy
- `is_satellite_only`: Whether connection is satellite-only

### SecurityEvent

Dataclass representing a security event.

**Attributes:**
- `event_type`: Type of event (EventType enum)
- `timestamp`: When the event occurred
- `security_level`: Associated security level
- `source`: Source component
- `message`: Event description
- `data`: Additional event data (dict)
- `event_id`: Unique identifier

**Methods:**
- `to_dict()`: Convert event to dictionary

### SecurityEventQueue

Thread-safe queue for managing security events.

**Methods:**
- `put(event)`: Add event to queue
- `get()`: Retrieve event from queue
- `register_handler(event_type, handler)`: Register event handler
- `unregister_handler(event_type, handler)`: Remove event handler
- `process_events()`: Async event processing (async)
- `get_history(event_type, security_level, limit)`: Get filtered event history
- `clear_history()`: Clear event history

### EncryptionManager

Manages encryption and decryption of sensitive data.

**Methods:**
- `__init__(key)`: Create with specific key
- `from_password(password, salt)`: Create from password (classmethod)
- `encrypt(data)`: Encrypt bytes
- `decrypt(encrypted_data)`: Decrypt bytes
- `encrypt_str(data)`: Encrypt string
- `decrypt_str(encrypted_data)`: Decrypt string
- `rotate_key(new_key)`: Rotate encryption key
- `re_encrypt(encrypted_data, new_key)`: Re-encrypt with new key

**Properties:**
- `key`: Current encryption key
- `salt`: Salt used for key derivation (if applicable)

## License

Apache License 2.0 - See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting pull requests.

## Security Considerations

- Always use strong passwords for password-based encryption
- Securely store encryption keys and salts
- Regularly rotate encryption keys for sensitive data
- Monitor security events and respond to critical alerts promptly
- Use appropriate security levels based on threat assessment

## Usage Examples

### Run comprehensive audit
```bash
python secure_it_infra.py --audit --config config.json
```

### Generate audit with recommendations
```bash
python secure_it_infra.py --audit --recommendations
```

### Check specific security domains
```bash
python secure_it_infra.py --check-network --check-encryption
```

### Save report to file
```bash
python secure_it_infra.py --audit --output security_report.json
```

Enterprise-grade security infrastructure for organizations leveraging Starlink satellite connectivity in rural and remote deployments.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

## Overview

**secure-it-infra-Starlink** provides a comprehensive collection of enterprise-grade security tools and frameworks designed to strengthen IT infrastructure security in environments utilizing Starlink satellite connectivity. This solution ensures that organizations operating in rural or remote areas can maintain robust, scalable, and secure IT operations while meeting compliance requirements.

### Key Features

- 🔒 **Enterprise-Grade Security Modules** - Network security, access control, encryption, and threat detection
- 🛰️ **Starlink Integration** - Optimized configurations for satellite connectivity
- 📊 **Compliance Frameworks** - SOC 2, ISO 27001, and GDPR compliance support
- 🔍 **Monitoring & Detection** - Real-time threat monitoring and intrusion detection
- 🏗️ **Reference Architectures** - Proven patterns for secure rural/remote deployments
- 📚 **Comprehensive Documentation** - Integration guides, best practices, and examples

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink

# No dependencies required - ready to use!
```

### Basic Usage

```python
from modules import (
    FirewallRuleManager,
    VPNManager,
    MFAManager,
    EncryptionManager
)

# Configure firewall for Starlink
firewall = FirewallRuleManager()
firewall.configure_starlink_access()

# Setup VPN optimized for satellite connectivity
vpn = VPNManager()
vpn.optimize_for_starlink()

# Enable multi-factor authentication
mfa = MFAManager()
mfa.register_user('user_001', 'admin', mfa_method='totp')

# Configure encryption
encryption = EncryptionManager()
encryption.enable_tls_for_starlink()
```

### Running Examples

```bash
# Basic security setup
python3 examples/basic_setup.py

# Multi-site deployment
python3 examples/multi_site_deployment.py

# Compliance monitoring
python3 examples/compliance_monitoring.py
```

## Architecture

The security framework is built with a modular architecture:

```
security_modules/
├── __init__.py           # Module exports
├── network_monitor.py    # Network monitoring functionality
├── threat_detector.py    # Threat detection and analysis
├── policy_enforcer.py    # Policy management and enforcement
├── incident_responder.py # Incident response automation
├── vpn_manager.py        # VPN connectivity management
└── backup_manager.py     # Backup and failover management
```

## Features

### Network Monitor
- Network device discovery
- Port scanning capabilities
- Real-time anomaly detection
- Network traffic analysis

### Threat Detector
- Integration with threat intelligence feeds
- Automated log analysis
- Malware detection and scanning
- IP reputation checking
- Threat reporting and tracking

### Policy Enforcer
- Dynamic security level management
- Rule-based access control
- Automated policy enforcement
- Custom policy support
- Policy violation tracking

### Incident Responder
- Automated incident detection
- Playbook-based response automation
- Incident lifecycle management
- Custom playbook support
- Response action tracking

### VPN Manager
- Multi-protocol VPN support (OpenVPN, WireGuard, IPSec)
- Connection management and monitoring
- Automatic failover capabilities
- Traffic statistics and logging

### Backup Manager
- Multiple backup types (Full, Incremental, Differential, Snapshot)
- Backup encryption and verification
- Automated restore capabilities
- High-availability failover management
- Redundancy checking

## Security Levels

The Policy Enforcer supports five security levels:

1. **MINIMAL** - Basic security controls
2. **LOW** - Standard authentication required
3. **MEDIUM** - Multi-factor authentication, device control
4. **HIGH** - Restricted network access, strict firewall rules
5. **MAXIMUM** - Lockdown mode, whitelist-only access

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on GitHub.

## Disclaimer

This security framework provides foundational structures for security operations. In production environments, integrate with actual security tools and services for full functionality.
### Security Modules

#### 1. Network Security
- **Firewall Management** - Enterprise firewall rules optimized for Starlink
- **VPN Configuration** - WireGuard-based VPN with satellite optimization
- **Geo-Fencing** - Geographic access controls for remote locations

#### 2. Access Control
- **Multi-Factor Authentication (MFA)** - TOTP, SMS, hardware token, and biometric support
- **Role-Based Access Control (RBAC)** - Pre-configured enterprise roles
- **Risk-Based Authentication** - Contextual access decisions

#### 3. Encryption
- **Data at Rest** - AES-256-GCM encryption for storage
- **Data in Transit** - TLS 1.3 with optimized cipher suites
- **Key Management** - Automated rotation and secure storage

#### 4. Threat Detection
- **Intrusion Detection System (IDS)** - Real-time threat monitoring
- **Behavioral Analysis** - AI-powered anomaly detection
- **Security Monitoring** - 24/7 continuous monitoring with SIEM integration

### Reference Architectures

1. **Hub-and-Spoke** - Multiple remote sites connecting to central headquarters
2. **Mesh Network** - Direct site-to-site communication
3. **Zero Trust** - Identity-centric security for maximum protection
4. **Defense in Depth** - Layered security for high-value assets

## Documentation

### Core Documentation

- **[Starlink Integration Guide](docs/starlink_integration.md)** - Complete guide for integrating Starlink connectivity
- **[Security Architecture](docs/architecture.md)** - Reference architectures for rural/remote deployments
- **[Compliance Framework](docs/compliance.md)** - SOC 2, ISO 27001, and GDPR compliance guidance

### Configuration

- **[Network Configuration](config/starlink_network_config.yaml)** - Network topology and settings
- **[Security Policy](config/security_policy.json)** - Enterprise security policies

### Examples

- **[Basic Setup](examples/basic_setup.py)** - Getting started with security modules
- **[Multi-Site Deployment](examples/multi_site_deployment.py)** - Managing multiple remote locations
- **[Compliance Monitoring](examples/compliance_monitoring.py)** - Compliance checking and reporting

## Use Cases

### Rural Healthcare
- HIPAA-compliant telemedicine infrastructure
- Secure patient data transmission over Starlink
- 24/7 availability for emergency services

### Remote Mining Operations
- Operational technology (OT) security
- SCADA system protection
- Harsh environment deployments

### Agricultural Research
- Intellectual property protection
- IoT device management for sensors
- Cloud collaboration tools

### Emergency Services
- Disaster recovery communications
- Mobile command centers
- Rapid deployment scenarios

## Compliance

### Supported Frameworks

#### SOC 2 Type II
- Security, Availability, Confidentiality controls
- Continuous monitoring and audit logging
- Incident response procedures

#### ISO 27001
- Information Security Management System (ISMS)
- Risk assessment and treatment
- 93 security controls implementation

#### GDPR
- Data protection by design and default
- Privacy controls and data subject rights
- Cross-border data transfer safeguards

### Audit Support
- Automated compliance checking
- Pre-configured security policies
- Comprehensive audit logging
- Regular compliance reporting

## Features

### Network Security
- ✅ Stateful firewall with deep packet inspection
- ✅ VPN with MTU optimization for Starlink
- ✅ Persistent keepalive for satellite handoffs
- ✅ QoS traffic prioritization
- ✅ Geo-blocking and IP whitelisting

### Access Control
- ✅ Multi-factor authentication (MFA)
- ✅ Role-based access control (RBAC)
- ✅ Session management and timeout
- ✅ Risk-based authentication
- ✅ Privileged access management

### Data Protection
- ✅ AES-256 encryption at rest
- ✅ TLS 1.3 encryption in transit
- ✅ Automated key rotation
- ✅ End-to-end encryption
- ✅ Data loss prevention (DLP)

### Monitoring
- ✅ Real-time threat detection
- ✅ SIEM integration
- ✅ Behavioral analysis with ML
- ✅ 24/7 security monitoring
- ✅ Automated incident response

### Starlink Optimization
- ✅ Latency-optimized protocols
- ✅ Bandwidth management
- ✅ Connection resilience during handoffs
- ✅ Satellite-specific QoS
- ✅ Failover to backup connectivity

## Requirements

### Hardware
- Starlink Business Terminal (Gen 2 or higher)
- Enterprise router with VPN support
- Firewall appliance (hardware or software)
- Backup connectivity (4G/5G recommended)

### Software
- Python 3.8 or higher (for security modules)
- Network management system
- SIEM solution (for monitoring)
- Endpoint protection platform

### Connectivity
- Clear sky view for Starlink terminal
- Stable power supply with UPS
- Minimum 100 Mbps bandwidth per site

## Best Practices

1. **Always Use VPN** - Encrypt all traffic over Starlink
2. **Enable MFA** - Require multi-factor authentication for all users
3. **Monitor Continuously** - Implement 24/7 security monitoring
4. **Test Failover** - Regular testing of backup connectivity
5. **Update Regularly** - Keep firmware and security policies current
6. **Document Everything** - Maintain configuration documentation
7. **Regular Audits** - Conduct quarterly security assessments
8. **Backup Connectivity** - Always have cellular or fiber backup
9. **Encrypt Data** - Both at rest and in transit
10. **Train Staff** - Regular security awareness training

## Project Structure

```
secure-it-infra-Starlink/
├── modules/                    # Security modules
│   ├── network_security/      # Firewall and VPN
│   ├── access_control/        # MFA and RBAC
│   ├── encryption/            # Data protection
│   └── threat_detection/      # IDS and monitoring
├── config/                    # Configuration templates
│   ├── starlink_network_config.yaml
│   └── security_policy.json
├── docs/                      # Documentation
│   ├── starlink_integration.md
│   ├── architecture.md
│   └── compliance.md
├── examples/                  # Usage examples
│   ├── basic_setup.py
│   ├── multi_site_deployment.py
│   └── compliance_monitoring.py
├── README.md
└── LICENSE
```

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass
2. Code follows the project style guide
3. Security best practices are followed
4. Documentation is updated

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

Future enhancements planned:
- [ ] Integration with popular SIEM systems
- [ ] Advanced anomaly detection using ML
- [ ] Automated threat response capabilities
- [ ] Dashboard and visualization tools
- [ ] Mobile app for alerts and monitoring
- [ ] Cloud provider integrations (AWS, Azure, GCP)

---

**Note**: This toolkit is designed specifically for Starlink-connected enterprise infrastructures but can be adapted for other satellite or network environments.
- Code follows existing style
- New checks are modular and documented
- Configuration options are added for new features
- Security recommendations are actionable

## License

See LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Version

Current version: 1.0.0
## Changelog

### Version 1.0.0
- Initial release with comprehensive security auditing
- Starlink-specific optimizations
- Modular architecture
- JSON configuration support
- Detailed logging and reporting
Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or support:
- Open an issue on GitHub
- Review the documentation in `/docs/`
- Check examples in `/examples/`

## Security

If you discover a security vulnerability, please send an email to the maintainers. Do not open a public issue.

## Acknowledgments

- Starlink for satellite connectivity technology
- Enterprise security community for best practices
- Open source security tools and frameworks

---

**Built for enterprise security in rural and remote locations. Deploy with confidence.** 🛰️ 🔒
