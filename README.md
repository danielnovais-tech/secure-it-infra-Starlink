# Secure IT Infrastructure - Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Features

- **Real-time Security Monitoring**: Continuous monitoring of security metrics and status
- **Event Processing**: Asynchronous event queue for handling security alerts
- **Threat Detection**: Automated threat level assessment
- **Metrics Collection**: Performance and security metrics tracking

## Main Monitoring Loop

The system features a robust asynchronous monitoring loop that runs continuously:

```python
# Main monitoring loop
while self.running:
    try:
        await self._update_metrics()
        await self._check_security_status()
        await self._process_events()
        await asyncio.sleep(5)  # Main loop interval
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
```

See [MONITORING.md](MONITORING.md) for detailed documentation.

## Quick Start

### Running the Monitor

```bash
# Run the security monitor
python -m src.security_monitor
```

### Testing

```bash
# Run the test script
python test_monitor.py
```

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   └── security_monitor.py     # Main monitoring implementation
├── test_monitor.py              # Test script
├── MONITORING.md                # Detailed monitoring documentation
├── requirements.txt
└── README.md
```

## Documentation

- [MONITORING.md](MONITORING.md) - Detailed monitoring system documentation
- [LICENSE](LICENSE) - Apache 2.0 License

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Overview

This repository contains the foundational Terraform configuration for deploying and managing secure enterprise infrastructure for Starlink connectivity. It provides a comprehensive, production-ready setup with best practices for AWS infrastructure management.

## Features

- **Multi-Provider Setup**: Comprehensive provider configuration including AWS, Random, Null, Time, and TLS
- **Multi-Region Support**: Primary and secondary region configuration for disaster recovery
- **Remote State Management**: S3 backend with DynamoDB state locking
- **Default Tagging**: Automatic resource tagging for cost allocation and compliance
- **Environment Separation**: Support for dev, staging, and production environments
- **Security Best Practices**: Encrypted state, least privilege, and secure defaults

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.5.0
- AWS CLI configured with appropriate credentials
- An AWS account with necessary permissions

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
   cd secure-it-infra-Starlink
   ```

2. **Configure variables**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your specific values
   ```

3. **Initialize Terraform**
   ```bash
   terraform init
   ```

4. **Review the plan**
   ```bash
   terraform plan
   ```

5. **Apply the configuration**
   ```bash
   terraform apply
   ```

## Project Structure

```
.
├── backend.tf              # Remote state backend configuration
├── main.tf                 # Main infrastructure resources and data sources
├── outputs.tf              # Output values for the infrastructure
├── providers.tf            # Provider configurations
├── variables.tf            # Input variable definitions
├── versions.tf             # Terraform and provider version constraints
├── terraform.tfvars.example # Example variable values
└── README.md              # This file
# Secure IT Infrastructure for Starlink
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

## Overview

This repository provides infrastructure components for reliable and scalable fleet management of Starlink enterprise deployments. It includes:

- **Apache Pulsar**: Distributed messaging and streaming platform for reliability integrations
- **Armada Atlas**: Multi-cluster batch job scheduler for fleet management

## Features

### Apache Pulsar for Reliability Integrations

- **Message Persistence**: Durable storage with configurable retention policies
- **Deduplication**: Exactly-once message delivery semantics
- **Multi-tenancy**: Isolated namespaces for different teams and services
- **Geo-replication**: Cross-datacenter message replication for disaster recovery
- **High Availability**: Fault-tolerant architecture with automatic failover

### Armada Atlas for Fleet Management

- **Multi-cluster Scheduling**: Manage batch jobs across multiple Kubernetes clusters
- **Fair Resource Allocation**: Queue-based fair sharing of cluster resources
- **Priority Scheduling**: Support for job priorities and preemption
- **High Throughput**: Handle thousands of jobs per second
- **Integrated Monitoring**: Web UI for job visibility and cluster management

### Integration Benefits

- **Reliable Event Streaming**: Job events are reliably streamed through Pulsar
- **Complete Audit Trail**: All job lifecycle events are persisted
- **Scalable Architecture**: Horizontal scaling of both compute and messaging layers
- **Production Ready**: Battle-tested components used by large-scale organizations

## Quick Start

Get started quickly with Docker Compose:

```bash
# Start Pulsar
cd pulsar
docker-compose up -d

# Start Armada Atlas
cd ../armada-atlas
docker-compose up -d
```

Access the UIs:
- **Pulsar Manager**: http://localhost:9527
- **Armada Lookout**: http://localhost:8089

For detailed instructions, see the [Quick Start Guide](docs/QUICKSTART.md).

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- [Integration Guide](docs/INTEGRATION.md) - Detailed architecture and integration patterns
- [Security Configuration Guide](docs/SECURITY.md) - **Production security hardening (REQUIRED reading)**
- [Pulsar Documentation](pulsar/README.md) - Apache Pulsar setup and configuration
- [Armada Atlas Documentation](armada-atlas/README.md) - Armada setup and usage

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Starlink Infrastructure                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         Armada Atlas Server             │
        │      (Fleet Management Control)         │
        └──────────┬──────────────────────────────┘
                   │
                   │ Publishes job events
                   ▼
        ┌─────────────────────────────────────────┐
        │         Apache Pulsar Cluster           │
        │      (Reliable Event Streaming)         │
        └──────────┬──────────────────────────────┘
                   │
                   │ Consumes events
                   ▼
        ┌─────────────────────────────────────────┐
        │      Event Consumers & Analytics        │
        └─────────────────────────────────────────┘
```

## Repository Structure

```
.
├── pulsar/                          # Apache Pulsar configuration
│   ├── docker-compose.yml          # Docker Compose deployment
│   ├── kubernetes-deployment.yaml  # Kubernetes deployment
│   ├── broker.conf                 # Broker configuration
│   └── README.md                   # Pulsar documentation
│
├── armada-atlas/                    # Armada Atlas configuration
│   ├── docker-compose.yml          # Docker Compose deployment
│   ├── kubernetes-deployment.yaml  # Kubernetes deployment
│   ├── config/                     # Configuration files
│   │   ├── armada-server-config.yaml
│   │   ├── armada-executor-config.yaml
│   │   ├── lookout-config.yaml
│   │   └── lookout-ingester-config.yaml
│   └── README.md                   # Armada documentation
│
└── docs/                            # Documentation
    ├── QUICKSTART.md               # Quick start guide
    └── INTEGRATION.md              # Integration guide
```

## Deployment Options

### Docker Compose (Development/Testing)

Suitable for local development and testing:

```bash
# See Quick Start Guide for detailed instructions
cd pulsar && docker-compose up -d
cd ../armada-atlas && docker-compose up -d
```

### Kubernetes (Production)

Suitable for production deployments:

```bash
# Deploy Pulsar
kubectl apply -f pulsar/kubernetes-deployment.yaml

# Deploy Armada
kubectl apply -f armada-atlas/kubernetes-deployment.yaml
```

See individual component READMEs for detailed deployment instructions.

## Security Considerations

⚠️ **IMPORTANT**: The default configurations are for development and testing only!

For production deployments, ensure you:

1. **Enable TLS Encryption**: Encrypt data in transit for both Pulsar and Armada
2. **Configure Authentication**: Use token-based or certificate-based authentication
3. **Enable Authorization**: Implement role-based access control (RBAC)
4. **Secure Secrets**: Use Kubernetes Secrets or a secrets management solution (Vault, AWS Secrets Manager, etc.)
5. **Change Default Passwords**: All default passwords must be changed
6. **Network Policies**: Restrict network access between components
7. **Regular Updates**: Keep all components updated with security patches

**See the comprehensive [Security Configuration Guide](docs/SECURITY.md) for detailed hardening instructions.**

## Monitoring

Both components expose Prometheus metrics:

- **Pulsar Broker**: `http://broker:8080/metrics`
- **Armada Server**: `http://armada-server:9000/metrics`
- **Armada Executor**: `http://armada-executor:9001/metrics`

Key metrics to monitor:
- Job submission and completion rates
- Message ingress/egress throughput
- Resource utilization across clusters
- Event processing lag
- System health and availability

## Contributing

Contributions are welcome! Please:
This project provides a Network Security Monitor for Starlink infrastructure that tracks key network and security metrics including:
- Latency (ms)
- Jitter (ms)
- Packet Loss (%)
- Throughput (Mbps)

## Features

- **Real-time Metrics Monitoring**: Continuously monitors network performance metrics
- **Security Scanning**: Periodic security threat scanning
- **Alert Monitoring**: Detects anomalies and triggers warnings for high latency and packet loss
- **Graceful Shutdown**: Properly manages module lifecycles with error handling

## Usage

Run the network security monitor:

```bash
python main.py
```

Or import as a module:

```python
from src.network_security_monitor import NetworkSecurityMonitor
import asyncio

async def run():
    monitor = NetworkSecurityMonitor()
    try:
        await monitor.start()
    finally:
        await monitor.stop()

asyncio.run(run())
This repository provides a comprehensive security monitoring system for Starlink infrastructure, including:
- Real-time security score calculation based on multiple factors
- Connection stability monitoring
- Network quality metrics tracking
- Authentication security monitoring

## Features

- **Security Score Calculation**: Weighted scoring based on:
  - Encryption strength (40%)
  - Failed authentication attempts (30%)
  - Connection stability (20%)
  - Signal quality (10%)

- **Connection Stability Calculation**: Weighted scoring based on:
  - Uptime percentage (40%)
  - Packet loss rate (30%)
  - Signal quality (20%)
  - Network latency (10%)

- **Comprehensive Metrics Tracking**:
  - Signal quality
  - Network latency
  - Packet loss rate
  - Uptime percentage
  - Failed authentication attempts
  - Encryption strength

## Installation

No external dependencies required. The system uses only Python standard library.

```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

## Usage

### Basic Usage

```python
from starlink_monitor import StarlinkMonitor

# Initialize the monitor
monitor = StarlinkMonitor()

# Update metrics
monitor.update_metrics(
    signal_quality=92.0,
    latency_ms=35.0,
    packet_loss_rate=0.5,
    uptime_percentage=99.0,
    failed_auth_attempts=1,
    encryption_strength=98.0
)

# Get status report
report = monitor.get_status_report()
print(f"Security Score: {report['security_score']:.2f}")
print(f"Connection Stability: {report['connection_stability']:.2f}")
```

### Running the Example

```bash
python example_usage.py
```

## Testing

Run the comprehensive test suite:

```bash
python -m unittest test_starlink_monitor -v
## Security Scoring System

This repository includes a comprehensive security scoring system that adjusts scores based on security levels with advanced features including configurable multipliers, audit trails, export capabilities, historical tracking, and schema validation.

### Features

- **Security Level Management**: Support for CRITICAL, ELEVATED, and NORMAL security levels
- **Score Adjustment**: Automatic score adjustment based on security level
  - CRITICAL: 70% of base score (0.7x multiplier)
  - ELEVATED: 90% of base score (0.9x multiplier)
  - NORMAL: 100% of base score (no adjustment)
- **Configurable Multipliers**: Override default multipliers via:
  - Custom multipliers dictionary
  - JSON configuration file with schema validation
  - Validates multipliers (non-negative, numeric)
  - Warns on unusual values (e.g., multipliers > 2.0)
- **Audit Trail**: Complete audit trail of all scoring operations with:
  - Reason for adjustment
  - Points change details
  - Original and adjusted scores
  - Security level applied
  - ISO timestamps
  - Historical comparison data
  - Configurable detail levels (summary/full)
- **Audit Trail Export**:
  - Export to JSON format for downstream analytics
  - Export to CSV format for dashboards and reporting
  - Preserves all audit metadata
- **Historical Comparison**:
  - Track score changes over time
  - Automatic delta calculation from previous runs
  - Narrative descriptions of changes
- **Boundary Handling**:
  - Zero scores remain zero regardless of multiplier
  - Optional max score cap for very high scores
  - Graceful handling of unknown security levels (defaults to 1.0x)
- **Input Validation**: 
  - Prevents negative base scores with appropriate error handling
  - Schema validation for configuration files
  - Clear error messages for misconfiguration

### Installation

No additional dependencies required. Uses Python 3.12+.

### Usage

#### Basic Usage

```python
from security_scoring import SecurityLevel, SecurityScorer

# Create a scorer with a security level
scorer = SecurityScorer(SecurityLevel.CRITICAL)

# Calculate adjusted score
base_score = 100.0
adjusted_score = scorer.calculate_score(base_score)
print(f"Adjusted Score: {adjusted_score}")  # Output: 70.0
```

#### Using Custom Multipliers

```python
# Define custom multipliers
custom_multipliers = {
    SecurityLevel.CRITICAL: 0.5,
    SecurityLevel.ELEVATED: 0.75,
}

scorer = SecurityScorer(SecurityLevel.CRITICAL, custom_multipliers=custom_multipliers)
score = scorer.calculate_score(100.0)  # Returns 50.0
```

#### Using Configuration File

Create a `config.json` file:
```json
{
  "multipliers": {
    "critical": 0.6,
    "elevated": 0.85,
    "normal": 1.0
  }
}
```

Then use it:
```python
scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file="config.json")
score = scorer.calculate_score(100.0)
```

#### Audit Trail Integration

```python
scorer = SecurityScorer(SecurityLevel.CRITICAL)
scorer.calculate_score(100.0)
scorer.calculate_score(250.0)

# Get audit trail with full detail
audit_trail = scorer.get_audit_trail(detail_level="full")
for entry in audit_trail:
    print(entry)
    # Output includes: reason, points, security_level, original_score,
    #                  adjusted_score, timestamp, and historical_delta

# Get summary view
summary = scorer.get_audit_trail(detail_level="summary")
# Returns only reason and adjusted_score for each entry
```

**Example Output - Full Detail:**
```python
[
  {
    'reason': 'CRITICAL security level multiplier',
    'points': '-30.0 (0.7x applied)',
    'security_level': 'critical',
    'original_score': 100.0,
    'adjusted_score': 70.0,
    'timestamp': '2026-01-15T16:00:00.123456'
  },
  {
    'reason': 'CRITICAL security level multiplier',
    'points': '-75.0 (0.7x applied)',
    'security_level': 'critical',
    'original_score': 250.0,
    'adjusted_score': 175.0,
    'timestamp': '2026-01-15T16:00:01.234567'
  }
]
```

**Example Output - Summary Detail:**
```python
[
  {'reason': 'CRITICAL security level multiplier', 'adjusted_score': 70.0},
  {'reason': 'CRITICAL security level multiplier', 'adjusted_score': 175.0}
]
```

#### Historical Comparison

```python
scorer = SecurityScorer(SecurityLevel.ELEVATED)

# Track changes over multiple runs
previous_score = None
for base in [100.0, 120.0, 90.0]:
    current = scorer.calculate_score(base, previous_score=previous_score)
    previous_score = current

# Audit trail includes historical deltas
trail = scorer.get_audit_trail()
# Entry format: "ELEVATED security level multiplier (Score increased by 18.0 compared to last run)"
```

**Example Output:**
```python
[
  {
    'reason': 'ELEVATED security level multiplier',
    'points': '-10.0 (0.9x applied)',
    'security_level': 'elevated',
    'original_score': 100.0,
    'adjusted_score': 90.0,
    'timestamp': '2026-01-15T16:00:00.000000'
  },
  {
    'reason': 'ELEVATED security level multiplier (Score increased by 18.0 compared to last run)',
    'points': '-12.0 (0.9x applied)',
    'security_level': 'elevated',
    'original_score': 120.0,
    'adjusted_score': 108.0,
    'timestamp': '2026-01-15T16:00:01.000000',
    'previous_score': 90.0,
    'historical_delta': 18.0
  },
  {
    'reason': 'ELEVATED security level multiplier (Score decreased by 27.0 compared to last run)',
    'points': '-9.0 (0.9x applied)',
    'security_level': 'elevated',
    'original_score': 90.0,
    'adjusted_score': 81.0,
    'timestamp': '2026-01-15T16:00:02.000000',
    'previous_score': 108.0,
    'historical_delta': -27.0
  }
]
```

#### Exporting Audit Trail

```python
scorer = SecurityScorer(SecurityLevel.CRITICAL)
scorer.calculate_score(100.0, previous_score=120.0)
scorer.calculate_score(250.0, previous_score=180.0)

# Export to JSON for analytics
scorer.export_audit_trail_json("audit_log.json", detail_level="full")

# Export to CSV for dashboards
scorer.export_audit_trail_csv("audit_log.csv")
```

**JSON Export Example Output:**
```json
{
  "security_level": "critical",
  "export_timestamp": "2026-01-15T16:00:00.000000",
  "entries": [
    {
      "reason": "CRITICAL security level multiplier (Score decreased by 50.0 compared to last run)",
      "points": "-30.0 (0.7x applied)",
      "security_level": "critical",
      "original_score": 100.0,
      "adjusted_score": 70.0,
      "timestamp": "2026-01-15T16:00:00.000000",
      "previous_score": 120.0,
      "historical_delta": -50.0
    },
    {
      "reason": "CRITICAL security level multiplier (Score increased by 5.0 compared to last run)",
      "points": "-75.0 (0.7x applied)",
      "security_level": "critical",
      "original_score": 250.0,
      "adjusted_score": 175.0,
      "timestamp": "2026-01-15T16:00:01.000000",
      "previous_score": 180.0,
      "historical_delta": -5.0
    }
  ]
}
```

**CSV Export Example Output:**
```csv
timestamp,reason,points,security_level,original_score,adjusted_score,previous_score,historical_delta
2026-01-15T16:00:00.000000,CRITICAL security level multiplier (Score decreased by 50.0 compared to last run),-30.0 (0.7x applied),critical,100.0,70.0,120.0,-50.0
2026-01-15T16:00:01.000000,CRITICAL security level multiplier (Score increased by 5.0 compared to last run),-75.0 (0.7x applied),critical,250.0,175.0,180.0,-5.0
```

#### Configuration File with Schema Validation

Create a `config.json` file with validation:
```json
{
  "multipliers": {
    "critical": 0.6,
    "elevated": 0.85,
    "normal": 1.0
  }
}
```

The system validates:
- All security levels are valid (critical, elevated, normal)
- All multipliers are numeric
- All multipliers are non-negative
- Warns if multipliers are unusually high (> 2.0)

```python
from security_scoring import SecurityScorer, ConfigValidationError

try:
    scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file="config.json")
    score = scorer.calculate_score(100.0)
except ConfigValidationError as e:
    print(f"Invalid configuration: {e}")
```

#### Boundary Cases

```python
scorer = SecurityScorer(SecurityLevel.CRITICAL)

# Zero score remains zero
zero_score = scorer.calculate_score(0.0)  # Returns 0.0

# Very high score with max cap
capped_score = scorer.calculate_score(10000.0, max_score=500.0)  # Returns 500.0

# Very high score without cap
uncapped_score = scorer.calculate_score(10000.0)  # Returns 7000.0
```

### Running Examples

```bash
python3 example.py
```

### Running Tests

```bash
python3 -m unittest test_security_scoring.py -v
```

All 34 tests should pass, including:
- Config schema validation tests
- Audit trail export tests (JSON/CSV)
- Historical comparison tests
- Detail level tests
- Integration tests

### Files

- `security_scoring.py`: Main module with SecurityLevel enum, SecurityScorer class, AuditEntry class, and config validation
- `test_security_scoring.py`: Comprehensive unit tests (34 test cases) including integration tests
- `example.py`: Example usage demonstrations including all features (8 scenarios)
- `config.json`: Sample configuration file for custom multipliers
- `requirements.txt`: Project dependencies (Python 3.12+)

### API Reference

#### SecurityLevel (Enum)
- `CRITICAL`: Critical security level (default 0.7x multiplier)
- `ELEVATED`: Elevated security level (default 0.9x multiplier)
- `NORMAL`: Normal security level (1.0x multiplier)

#### SecurityScorer (Class)
- `__init__(security_level, custom_multipliers=None, config_file=None)`: Initialize scorer
  - Raises `ConfigValidationError` if config file is invalid
- `calculate_score(base_score, max_score=None, previous_score=None)`: Calculate adjusted score
  - `previous_score`: Optional previous score for historical comparison
- `get_audit_trail(detail_level="full")`: Get list of audit entries
  - `detail_level`: "summary" or "full"
- `clear_audit_trail()`: Clear the audit trail
- `export_audit_trail_json(filepath, detail_level="full")`: Export audit trail to JSON
- `export_audit_trail_csv(filepath)`: Export audit trail to CSV

#### AuditEntry (Class)
- `to_dict(detail_level="full")`: Convert audit entry to dictionary format
  - Returns different fields based on detail_level

#### Utility Functions
- `validate_config_schema(config)`: Validate configuration dictionary
  - Raises `ConfigValidationError` for invalid configs

### Integration Tests

The test suite includes integration tests that verify the complete workflow:

```python
# Example integration test workflow
scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file="config.json")
score1 = scorer.calculate_score(100.0)
score2 = scorer.calculate_score(250.0, previous_score=200.0)
score3 = scorer.calculate_score(500.0, max_score=400.0)
scorer.export_audit_trail_json("output.json")
scorer.export_audit_trail_csv("output.csv")
```

This ensures the entire pipeline (config loading → scoring → audit tracking → export) works correctly.

## Roadmap

### ✅ Implemented (Current Release)

- **Core Functionality**
  - Security level enumeration (CRITICAL, ELEVATED, NORMAL)
  - Score adjustment with configurable multipliers
  - Dictionary-based multiplier lookup
  
- **Configuration & Validation**
  - JSON configuration file support
  - Schema validation with `ConfigValidationError`
  - Custom multiplier overrides
  - Non-negative multiplier validation
  - Warnings for unusual values

- **Audit Trail System**
  - Complete audit logging with timestamps
  - Historical comparison tracking
  - Configurable verbosity levels (summary/full)
  - Export to JSON format
  - Export to CSV format
  
- **Robustness**
  - Input validation (negative score prevention)
  - Graceful handling of unknown security levels
  - Optional max score capping
  - Boundary case handling (zero scores, very high scores)
  
- **Testing & Quality**
  - 34 comprehensive unit tests
  - Integration tests for complete workflows
  - CodeQL security scanning (0 vulnerabilities)
  - Python 3.12+ compatibility

### 🔮 Planned (Future Enhancements)

- **Internationalization (i18n)**
  - Multi-language support for audit trail messages
  - Localized error messages
  
- **Dashboard Integration**
  - Real-time monitoring connectors
  - Grafana/Prometheus integration
  - REST API endpoints
  
- **Performance Optimization**
  - Benchmarking under high-volume scoring
  - Batch scoring operations
  - Async scoring support
  
- **Advanced Features**
  - Custom scoring algorithms
  - Machine learning-based threat level prediction
  - Automated threshold tuning
  
- **Enterprise Features**
  - Role-based access control
  - Multi-tenancy support
  - Compliance reporting (SOC2, ISO 27001)

### 💡 Contributions Welcome

We welcome contributions in any of the planned areas or new feature suggestions. Please open an issue to discuss major changes before submitting a pull request.
## Overview

This repository provides a comprehensive security monitoring solution for Starlink infrastructure, featuring real-time metric tracking, anomaly detection, and security scoring.

## Features

- **Real-time Security Monitoring**: Track security metrics in real-time
- **Significant Change Logging**: Automatically logs changes in metrics that exceed configurable thresholds
- **Anomaly Detection**: Detects and flags security anomalies based on predefined rules
- **Security Scoring**: Calculates an overall security score (0-100) based on current metrics
- **Flexible Alerting**: Supports severity-based filtering of security events

## Installation

## Starlink Connection Metrics Module

This module provides advanced functionality to monitor and calculate quality metrics for Starlink satellite internet connections based on packet loss and latency.

### Features

**Core Metrics:**
- **Connection Quality Scoring**: Calculate overall connection quality (0-100) based on configurable thresholds
- **Stability Scoring**: Advanced stability calculation that heavily penalizes packet loss (70% weight) and considers latency (30% weight)
- **Connection Status**: Get comprehensive status ("Excellent", "Good", "Fair", "Poor") based on quality and stability metrics
- **Input Validation**: Automatic validation of metrics to ensure data integrity

**Advanced Features:**
- **🆕 Configurable Thresholds**: Customize packet loss and latency thresholds for different environments (satellite, fiber, remote)
- **🆕 Dynamic Scaling**: Adjust latency ceiling and weights based on environment or SLA requirements
- **🆕 Historical Smoothing**: Sliding window averaging to reduce false positives from momentary spikes
- **🆕 Alert Integration**: Event-driven alerts when stability falls below configurable thresholds
- **🆕 Service Level Mapping**: Map technical metrics to business service levels (Stable, Degraded, Critical, Offline)

**Observability & Integration:**
- **📊 Prometheus Metrics Export**: Export metrics in Prometheus format for real-time dashboards
- **📊 CloudWatch Metrics Export**: Send metrics to AWS CloudWatch for monitoring
- **📋 Structured JSON Logging**: SIEM-compatible logging for security and audit
- **📈 Periodic Reporting**: Generate governance reports with SLA compliance checking
- **🧪 Integration Testing**: Comprehensive tests simulating real network scenarios and chaos conditions

### Installation

```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

### Usage

#### Quick Start

```python
from starlink_metrics import monitor_connection

# Monitor connection with current metrics
status = monitor_connection(packet_loss=3.0, latency=120.0)
print(f"Connection Status: {status['status']}")
print(f"Quality Score: {status['quality_score']}/100")
print(f"Stability Score: {status['stability_score']:.3f}")
print(f"Service Level: {status['service_level']}")
```

#### Advanced Usage with Custom Thresholds

```python
from starlink_metrics import (
    ConnectionMetrics, 
    StarlinkConnectionQuality,
    QualityThresholds,
    StabilityThresholds
)

# Create metrics object
metrics = ConnectionMetrics(packet_loss=5.0, latency=150.0)

# Configure custom thresholds for your environment
quality_thresholds = QualityThresholds(
    packet_loss_threshold=10.0,  # More lenient for satellite
    latency_threshold=200.0
)

stability_thresholds = StabilityThresholds(
    max_latency=600.0,  # Higher ceiling for satellite
    packet_loss_weight=0.7,
    latency_weight=0.3
)

# Create quality calculator with custom thresholds
quality = StarlinkConnectionQuality(
    metrics,
    quality_thresholds=quality_thresholds,
    stability_thresholds=stability_thresholds
)

# Get individual scores
quality_score = quality.calculate_quality_score()
stability_score = quality.calculate_stability_score()

# Get comprehensive status
status = quality.get_connection_status()
```

#### Alert Integration

```python
from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    AlertThresholds
)

# Define alert callback
def alert_handler(level, data):
    """Handle connection alerts."""
    print(f"Alert [{level}]: Stability={data['stability']:.3f}")
    print(f"Service Level: {data['service_level']}")
    if level == "critical":
        # Trigger failover mechanism (implement your own logic)
        # initiate_failover()
        pass

# Create quality monitor with alerts
metrics = ConnectionMetrics(packet_loss=25.0, latency=380.0)
quality = StarlinkConnectionQuality(
    metrics,
    alert_callback=alert_handler,
    alert_thresholds=AlertThresholds(
        critical_stability=0.3,  # Alert when < 0.3
        degraded_stability=0.5   # Warn when < 0.5
    )
)

status = quality.get_connection_status()
# Alert will be triggered automatically if thresholds are exceeded
```

#### Historical Smoothing

```python
from starlink_metrics import ConnectionMetrics, StarlinkConnectionQuality

# Enable 10-point sliding window for smoothing
quality = StarlinkConnectionQuality(
    ConnectionMetrics(packet_loss=5.0, latency=100.0),
    history_window_size=10
)

# Collect metrics over time
for measurement in measurements:
    quality.metrics = ConnectionMetrics(**measurement)
    
    # Get smoothed stability (averaged over history window)
    smoothed = quality.calculate_stability_score(use_smoothing=True)
    
    # Or get raw current value
    current = quality.calculate_stability_score(use_smoothing=False)
```

### Enhanced Features

#### 1. Configurable Thresholds

Adapt the monitoring system to different environments and SLA requirements:

```python
from starlink_metrics import QualityThresholds, StabilityThresholds

# Lenient thresholds for remote/satellite environments
lenient_quality = QualityThresholds(
    packet_loss_threshold=10.0,  # Allow up to 10% loss
    latency_threshold=250.0      # Allow up to 250ms latency
)

# Strict thresholds for critical applications
strict_quality = QualityThresholds(
    packet_loss_threshold=2.0,   # Low tolerance
    packet_loss_penalty=20.0,    # Heavy penalty
    latency_threshold=100.0,     # Low latency required
    latency_penalty=10.0
)
```

#### 2. Dynamic Scaling

Normalize latency expectations based on environment:

```python
# Satellite environment: higher latency tolerance
satellite_stability = StabilityThresholds(
    max_latency=800.0,           # Higher ceiling
    packet_loss_weight=0.8,      # Emphasize packet loss
    latency_weight=0.2
)

# Fiber environment: lower latency expectations
fiber_stability = StabilityThresholds(
    max_latency=100.0,           # Low ceiling
    packet_loss_weight=0.6,
    latency_weight=0.4           # Latency more important
)
```

#### 3. Service Level Mapping

Map technical metrics to business service levels:

- **STABLE**: Stability ≥ 0.7 (Production-ready)
- **DEGRADED**: Stability ≥ 0.5 (Reduced performance)
- **CRITICAL**: Stability ≥ 0.3 (Service at risk)
- **OFFLINE**: Stability < 0.3 (Service unavailable)

```python
status = quality.get_connection_status()
service_level = status['service_level']  # Returns: "Stable", "Degraded", "Critical", or "Offline"
```

#### 4. Historical Smoothing

Reduce false positives from momentary spikes:

```python
# Without smoothing: sensitive to individual measurements
# With smoothing: averaged over sliding window

quality = StarlinkConnectionQuality(
    metrics,
    history_window_size=10  # Average last 10 measurements
)
```

Benefits:
- Prevents false alarms from temporary fluctuations
- Provides more stable trend analysis
- Improves decision-making for automated systems

#### 5. Alert Integration

Facilitate proactive monitoring and failover:

```python
def alert_handler(level, data):
    """Example alert handler - implement your own logic."""
    if level == "critical":
        # trigger_failover()  # Implement your failover logic
        # send_notification("Critical: Connection failing")
        print(f"CRITICAL: Connection failing - {data}")
    elif level == "degraded":
        # send_notification("Warning: Connection degraded")
        print(f"WARNING: Connection degraded - {data}")
        
quality = StarlinkConnectionQuality(
    metrics,
    alert_callback=alert_handler
)
```

### Observability & Integration

#### Prometheus Metrics Export

Export metrics for Prometheus scraping:

```python
from observability import MetricsExporter

exporter = MetricsExporter()
metrics = ConnectionMetrics(packet_loss=5.0, latency=120.0)
quality = StarlinkConnectionQuality(metrics)
status = quality.get_connection_status()

# Export in Prometheus format
prometheus_metrics = exporter.export_prometheus(
    status,
    labels={"datacenter": "us-west-1", "instance": "starlink-01"}
)
print(prometheus_metrics)
# Output:
# starlink_connection_quality_score{datacenter="us-west-1",instance="starlink-01"} 90.0 1768439665135
# starlink_connection_stability_score{datacenter="us-west-1",instance="starlink-01"} 0.842 1768439665135
# ...
```

#### CloudWatch Metrics Export

Send metrics to AWS CloudWatch:

```python
from observability import MetricsExporter

exporter = MetricsExporter()
cloudwatch_data = exporter.export_cloudwatch(status, namespace="Production/Starlink")

# Send to CloudWatch using boto3
import boto3
cloudwatch = boto3.client('cloudwatch')
cloudwatch.put_metric_data(**cloudwatch_data)
```

#### Structured Logging for SIEM

Log events in JSON format for SIEM integration:

```python
from observability import StructuredLogger

logger = StructuredLogger("production")

# Log alerts
def logging_alert_handler(level, data):
    logger.log_alert(level, data)

quality = StarlinkConnectionQuality(
    metrics,
    alert_callback=logging_alert_handler
)

# Log status changes
logger.log_status_change("Good", "Fair", status)

# Log metrics snapshots
logger.log_metrics(status)

# Output (JSON):
# {"timestamp": "2026-01-15T01:00:00Z", "event_type": "connection_alert", 
#  "alert_level": "critical", "severity": "HIGH", ...}
```

#### Periodic Reporting

Generate governance reports with SLA compliance:

```python
from observability import PeriodicReporter

reporter = PeriodicReporter()

# Record metrics over time
for status in status_measurements:
    reporter.record_metrics(status)

# Generate report with SLA thresholds
report = reporter.generate_report(sla_thresholds={
    "quality_score": 85.0,
    "stability_score": 0.75
})

print(f"Uptime: {report['uptime_percentage']}%")
print(f"SLA Compliant: {report['sla_compliance']['quality_score']['compliant']}")

# Export to JSON file
reporter.export_report_json(report, "monthly_report.json")
```

### Metrics Explanation

#### Quality Score (0-100)

The quality score starts at 100 and applies configurable penalties:
- **Default: Packet Loss > 5%**: -10 points
- **Default: Latency > 150ms**: -5 points

Thresholds and penalties can be customized via `QualityThresholds`.

#### Stability Score (0.0-1.0)

The stability score uses a weighted calculation with configurable parameters:
- **Packet Loss Factor** (default 70% weight): `max(0, 1 - packet_loss * multiplier)`
- **Latency Factor** (default 30% weight): `max(0, 1 - latency / max_latency)`

Default formula: `stability = loss_factor * 0.7 + latency_factor * 0.3`

This heavily penalizes packet loss while considering latency (default 500ms threshold).
All parameters can be customized via `StabilityThresholds`.

#### Connection Status (Legacy)

Status is determined based on both quality and stability scores:
- **Excellent**: Quality ≥ 90 AND Stability ≥ 0.9
- **Good**: Quality ≥ 75 AND Stability ≥ 0.7
- **Fair**: Quality ≥ 50 AND Stability ≥ 0.5
- **Poor**: Below Fair thresholds

#### Service Level (Governance)

Service level classification for aligning with business expectations:
- **Stable**: Stability ≥ 0.7 (configurable via `AlertThresholds.stable_stability`)
- **Degraded**: Stability ≥ 0.5 (configurable via `AlertThresholds.degraded_stability`)
- **Critical**: Stability ≥ 0.3 (configurable via `AlertThresholds.critical_stability`)
- **Offline**: Stability < 0.3

### Running Tests

```bash
# Run all tests (74 tests total)
pytest test_starlink_metrics.py test_enhanced_features.py test_observability.py test_integration.py -v

# Run core tests only (21 tests)
pytest test_starlink_metrics.py -v

# Run enhanced feature tests only (22 tests)
pytest test_enhanced_features.py -v

# Run observability tests only (15 tests)
pytest test_observability.py -v

# Run integration tests only (16 tests)
pytest test_integration.py -v

# Run with coverage
pytest --cov=starlink_metrics --cov=observability --cov-report=html
```

### Examples

See comprehensive examples demonstrating all features:

```bash
# Basic usage examples
python3 example_usage.py

# Enhanced features demonstration
python3 enhanced_examples.py

# Observability and integration examples
python3 observability_examples.py
```

### Security

See [SECURITY.md](SECURITY.md) for security best practices including:
- Configuration protection and validation
- Secure logging practices
- Alert callback security
- Metrics export security
- Audit and compliance guidelines

```bash
# Basic usage examples
python3 example_usage.py

# Enhanced features demonstration
python3 enhanced_examples.py
```

### API Reference

#### `ConnectionMetrics`

Data class for storing connection metrics.

**Attributes:**
- `packet_loss` (float): Packet loss percentage (0-100)
- `latency` (float): Latency in milliseconds (≥ 0)

#### `QualityThresholds`

Configuration for quality score calculation.

**Attributes:**
- `packet_loss_threshold` (float): Packet loss % threshold (default: 5.0)
- `packet_loss_penalty` (float): Points to deduct (default: 10.0)
- `latency_threshold` (float): Latency ms threshold (default: 150.0)
- `latency_penalty` (float): Points to deduct (default: 5.0)

#### `StabilityThresholds`

Configuration for stability score calculation.

**Attributes:**
- `max_latency` (float): Latency ceiling in ms (default: 500.0)
- `packet_loss_weight` (float): Weight for packet loss factor (default: 0.7)
- `latency_weight` (float): Weight for latency factor (default: 0.3)
- `packet_loss_multiplier` (float): Multiplier for packet loss penalty (default: 2.0)

#### `AlertThresholds`

Configuration for alert triggering.

**Attributes:**
- `critical_stability` (float): Critical alert threshold (default: 0.3)
- `degraded_stability` (float): Degraded alert threshold (default: 0.5)
- `stable_stability` (float): Stable threshold (default: 0.7)

#### `ServiceLevel`

Enum for service level classification.

**Values:**
- `STABLE`: Production-ready connection
- `DEGRADED`: Reduced performance
- `CRITICAL`: Service at risk
- `OFFLINE`: Service unavailable

#### `StarlinkConnectionQuality`

Class for calculating connection quality and stability with advanced features.

**Constructor Parameters:**
- `metrics` (ConnectionMetrics): Current connection metrics
- `quality_thresholds` (QualityThresholds, optional): Custom quality thresholds
- `stability_thresholds` (StabilityThresholds, optional): Custom stability thresholds
- `alert_thresholds` (AlertThresholds, optional): Custom alert thresholds
- `alert_callback` (Callable, optional): Callback function for alerts `(level: str, data: dict) -> None`
- `history_window_size` (int, optional): Size of sliding window for smoothing (0 = disabled)

**Methods:**
- `calculate_quality_score()`: Returns quality score (0-100)
- `calculate_stability_score(use_smoothing=True)`: Returns stability score (0.0-1.0)
- `get_service_level(stability)`: Returns ServiceLevel enum
- `check_and_alert(stability)`: Check thresholds and trigger alerts
- `get_connection_status()`: Returns dict with comprehensive status

**Status Dictionary Keys:**
- `status`: Legacy status string ("Excellent", "Good", "Fair", "Poor")
- `quality_score`: Quality score (0-100)
- `stability_score`: Stability score (0.0-1.0)
- `service_level`: Service level string ("Stable", "Degraded", "Critical", "Offline")
- `packet_loss`: Current packet loss %
- `latency`: Current latency ms
- `alert_level` (optional): Alert level if triggered ("critical", "degraded")
- `stability_history_size` (optional): Number of historical measurements

#### `monitor_connection(packet_loss, latency)`

Convenience function to quickly monitor connection.

**Parameters:**
- `packet_loss` (float): Packet loss percentage (0-100)
- `latency` (float): Latency in milliseconds

**Returns:** Dictionary with connection status information

### License

Apache License 2.0 - See LICENSE file for details.

## Features

This system provides comprehensive network monitoring and security management for Starlink connections:

### Network Stability Monitoring
- Calculates network stability score (0-100) based on performance metrics
- Deducts points for high jitter (up to 30 points, using multiplier of 2)
- Deducts points for high packet loss (up to 40 points, using multiplier of 10)
- Ensures stability scores remain within valid bounds (0-100)
- Formula constants are configurable via class constants

### Anomaly Detection
- Monitors latency, jitter, packet loss, and throughput
- Triggers alerts when metrics exceed configured thresholds
- Provides detailed anomaly information in event data
- Uses default thresholds when configuration is missing

### Security Level Management
- Tracks overall security score
- Automatically adjusts security level (NORMAL, ELEVATED, CRITICAL)
- Triggers events when security level changes
- Thresholds:
  - CRITICAL: security_score < 50
  - ELEVATED: 50 ≤ security_score < 70
  - NORMAL: security_score ≥ 70

## Configuration

See `config.example.json` for a sample configuration file.

### Performance Thresholds

Default values (can be overridden in configuration):
- `max_latency`: Maximum acceptable latency in milliseconds (default: 100.0)
- `max_jitter`: Maximum acceptable jitter in milliseconds (default: 20.0)
- `max_packet_loss`: Maximum acceptable packet loss percentage (default: 5.0)
- `min_throughput`: Minimum acceptable throughput in Mbps (default: 50.0)

### Stability Calculation Constants

The stability calculation uses configurable class constants:
- `JITTER_MULTIPLIER`: 2 (each ms of jitter deducts 2 points)
- `JITTER_MAX_DEDUCTION`: 30 (maximum points deducted for jitter)
- `PACKET_LOSS_MULTIPLIER`: 10 (each % of packet loss deducts 10 points)
- `PACKET_LOSS_MAX_DEDUCTION`: 40 (maximum points deducted for packet loss)
## Overview

This repository provides a comprehensive security monitoring and incident response system designed for enterprise infrastructure. The system includes:

- **Security Event Management**: Track and log security events with severity levels
- **Policy Enforcement**: Apply security policies based on threat levels
- **Incident Response**: Automated response to critical and high-severity security events
- **Event Processing**: Asynchronous event queue processing

## Features

- **Multi-level Security Policies**: Support for low, medium, high, and critical security levels
- **Automated Incident Response**: Configurable response actions based on event severity
- **Event Logging**: Comprehensive logging of all security events
- **Async Processing**: Non-blocking event processing using Python asyncio

## Installation

No external dependencies required. This system uses only Python standard library.

```bash
# Clone the repository
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
# Python 3.7+ is required
python --version
```

## Usage

### Basic Example

```python
import asyncio
from src.security_monitor import SecurityMonitor

async def monitor_security():
    # Create a security monitor instance
    monitor = SecurityMonitor()
    
    # Update with initial metrics
    metrics = {
        "failed_login_attempts": 2,
        "unauthorized_access_attempts": 0,
        "network_intrusion_attempts": 0,
        "active_connections": 100
    }
    await monitor.update_metrics(metrics)
    
    # Get security score
    score = monitor.get_security_score()
    print(f"Security Score: {score}")
    
    # Get detected anomalies
    anomalies = monitor.get_anomalies()
    print(f"Anomalies: {len(anomalies)}")

asyncio.run(monitor_security())
```

### Running the Example

```bash
python example.py
```

## Security Metrics

The SecurityMonitor tracks various security metrics including:

- `failed_login_attempts`: Number of failed authentication attempts
- `unauthorized_access_attempts`: Number of unauthorized access attempts
- `network_intrusion_attempts`: Number of network intrusion attempts
- `active_connections`: Current number of active connections
- `encrypted_connections`: Number of encrypted connections

## Logging and Anomaly Detection

### Significant Change Logging

The system automatically logs significant changes in metrics:
- **Numeric metrics**: Changes ≥ 10% are logged as significant
- **Non-numeric metrics**: All changes are logged
- **New metrics**: First-time metrics are logged

### Anomaly Detection

Anomalies are automatically detected when:
- Failed login attempts exceed 5
- Any unauthorized access attempts occur (critical)
- Any network intrusion attempts occur (critical)

### Security Score Calculation

The security score starts at 100 and deductions are made based on:
- Failed login attempts: -2 points each (max -20)
- Unauthorized access attempts: -10 points each (max -30)
- Network intrusion attempts: -15 points each (max -40)
- Active anomalies: -5 points per critical, -2 points per high severity

## API Reference

### SecurityMonitor Class

#### Methods

- `async update_metrics(new_metrics: Dict[str, Any])`: Update security metrics and detect anomalies
- `get_security_score() -> float`: Calculate and return the current security score (0-100)
- `get_anomalies(severity: Optional[str] = None) -> List[Dict[str, Any]]`: Get detected anomalies, optionally filtered by severity
- `clear_anomalies()`: Clear all recorded anomalies
### Quick Start

Run the demo to see the system in action:

```bash
python examples/demo.py
```

### Basic Usage

```python
import asyncio
from security_manager import SecurityManager

async def main():
    # Initialize the security manager
    manager = SecurityManager()
    await manager.start()
    
    # Create a security event
    manager.create_and_queue_event(
        event_type="unauthorized_access",
        severity="critical",
        source="firewall",
        description="Multiple failed login attempts"
    )
    
    # Adjust security level
    await manager.adjust_security_level("high")
    
    # Stop the manager
    await manager.stop()
This repository contains the **Starlink Security Foundation**, an enterprise security management system for infrastructures using Starlink connectivity. It provides comprehensive security monitoring, event logging, and network management capabilities specifically designed for remote or rural enterprise deployments.

## Features

- **Security Event Logging**: Automatic logging of security events to monthly JSON files
- **Network Monitoring**: Continuous monitoring of network devices and open ports
- **Metrics Tracking**: Real-time tracking of latency, jitter, packet loss, and throughput
- **Security Scoring**: Automated calculation of security scores and connection stability
- **Intelligent Recommendations**: Contextual security recommendations based on current metrics
- **Threat Management**: Active threat tracking and management
- **Graceful Shutdown**: POSIX signal handling for clean daemon operation
## Starlink Security Foundation

A comprehensive, modular security monitoring system that provides:

- **Network Monitoring**: Detects unauthorized devices and monitors open ports
- **Threat Detection**: Analyzes threats using intelligence feeds and log analysis
- **Policy Enforcement**: Enforces security policies based on security levels
- **Performance Metrics**: Tracks system performance and event statistics
- **Structured Logging**: JSON-formatted logs for SIEM/ELK integration

## Architecture

The system is built with a modular architecture for maximum maintainability and scalability:

```
security/
├── __init__.py           # Package exports
├── types.py              # Common types and enumerations
├── logging_utils.py      # Structured JSON logging
├── metrics.py            # Performance metrics tracking
├── foundation.py         # Core security foundation
├── network_monitor.py    # Network monitoring module
├── threat_detector.py    # Threat detection module
└── policy_enforcer.py    # Policy enforcement module
```

### Key Features

#### 🎯 Modularity
- Each component is independent with clear interfaces
- Easy to maintain, test, and replace individual modules
- Supports future extensions without breaking existing functionality

#### 📊 Observability
- **Performance Metrics**: Response times, event counts, error rates
- **Structured Logging**: JSON-formatted logs compatible with SIEM systems (Splunk, ELK)
- **Real-time Monitoring**: Track system health and security events

#### 🛡️ Resilience
- Exponential backoff for failed threat intelligence feeds
- Graceful fallback mechanisms
- Comprehensive error handling with detailed logging

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
import asyncio
from starlink_monitor import StarlinkMonitor, NetworkMetrics

# Load configuration
config = {
    'starlink': {
        'performance_thresholds': {
            'max_latency': 100.0,
            'max_jitter': 20.0,
            'max_packet_loss': 5.0,
            'min_throughput': 50.0
        }
    }
}

# Create monitor instance
monitor = StarlinkMonitor(config)

# Register event handler
async def handle_event(event):
    print(f"Event: {event['type']} - {event['message']}")

monitor.event_handlers.append(handle_event)

# Update metrics
metrics = NetworkMetrics(
    latency=75.0,
    jitter=12.0,
    packet_loss=3.0,
    throughput=80.0,
    security_score=85.0
)
monitor.update_metrics(metrics)

# Run monitoring
await monitor.monitor()

# Check stability
stability = monitor.calculate_stability()
print(f"Network stability: {stability}%")
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_security_monitor.py -v
```

## Development

### Project Structure

```
secure-it-infra-Starlink/
├── src/
│   ├── __init__.py
│   └── security_monitor.py    # Main security monitoring module
├── tests/
│   ├── __init__.py
│   └── test_security_monitor.py  # Comprehensive test suite
├── example.py                 # Usage example
├── requirements.txt           # Project dependencies
├── setup.py                  # Package setup configuration
└── README.md                 # This file
```

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a pull request.

pytest test_starlink_monitor.py -v
```

The test suite includes:
- Network metrics initialization and serialization tests
- Stability calculation tests with various scenarios
- Anomaly detection tests for all threshold types
- Security level transition tests
- Configuration validation tests
- Integration tests

All 25 tests pass successfully.

### Running the Security System

```bash
python starlink_security.py
```

### Using Individual Modules

```python
from security import (
    StarlinkSecurityFoundation,
    NetworkMonitor,
    ThreatDetector,
    PolicyEnforcer,
    SecurityLevel
)

# Initialize foundation
foundation = StarlinkSecurityFoundation()

# Initialize components
network_monitor = NetworkMonitor(foundation)
threat_detector = ThreatDetector(foundation)
policy_enforcer = PolicyEnforcer(foundation)

# Start monitoring
network_monitor.initialize()
threat_detector.initialize()
policy_enforcer.initialize()

# Get metrics
metrics = foundation.get_metrics()
print(f"Total events: {metrics['total_events']}")
print(f"Uptime: {metrics['uptime_seconds']}s")
```

### Running Tests

```bash
pytest test_starlink_security.py -v
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
## Starlink Enterprise Security Foundation

A comprehensive security management system for Starlink enterprise connections with automatic failover, monitoring, and threat detection capabilities.

### Features

- **Connection Monitoring**: Continuous monitoring of connection metrics including packet loss, latency, and stability
- **Automatic Failover**: Intelligent failover to backup connections when primary connection degrades
- **Security Metrics**: Real-time security scoring and threat tracking
- **Multiple Connection Types**: Support for Starlink-only, failover, dual-WAN, and load-balanced configurations
- **CLI Interface**: Command-line tools for status checking, reporting, and daemon mode
- **Event Logging**: Comprehensive logging of all security and connection events
## Overview

This security infrastructure provides enterprise-grade security management for Starlink-based networks, including:

- **Policy Enforcement**: Dynamic security policy enforcement based on threat levels
- **Incident Response**: Automated incident detection and response
- **VPN Management**: Secure VPN connectivity monitoring and management
- **Backup Management**: Automatic failover to backup connections

## Components

### PolicyEnforcer
Manages and enforces security policies including:
- Firewall rules configuration
- Encryption requirements (TLS 1.3+)
- Traffic filtering based on security levels

### IncidentResponder
Handles security incidents with:
- Automated incident classification
- Response action execution
- Incident logging and tracking

### VPNManager
Ensures secure connectivity through:
- VPN status monitoring
- Automatic reconnection
- Connection health checks

### BackupManager
Provides connection redundancy via:
- Multiple backup connection support
- Automatic failover detection
- Priority-based backup activation
This repository provides security solutions and best practices for enterprise infrastructures utilizing Starlink connectivity. It includes documentation on recommended security tools and configurations to ensure robust protection for Starlink-based networks.

## Third-Party Security Tools

### Aavora
**Purpose:** Multi-user security enhancement

Aavora provides advanced multi-user security capabilities for Starlink deployments, enabling:
- Comprehensive user access management
- Role-based security controls
- Multi-tenant security isolation
- Enhanced authentication and authorization mechanisms

This tool is particularly valuable for enterprise environments where multiple users and teams require secure access to Starlink-connected resources.

### Cydome
**Purpose:** Cyber protection for connected environments (Maritime)

Cydome delivers specialized cyber protection designed for connected environments, with a focus on maritime applications. Key features include:
- Real-time threat detection and prevention
- Protection for maritime and remote connected systems
- Secure communication channels for critical infrastructure
- Network anomaly detection and response

Cydome is especially suited for maritime operations and other remote connected environments where Starlink connectivity is essential for operational continuity.

This repository provides a secure, multi-environment infrastructure setup for Starlink-based enterprise solutions. It implements a controlled deployment strategy that ensures changes are thoroughly tested before reaching production, minimizing service disruptions.

## Key Features

- 🏗️ **Multi-Environment Setup**: Separate dev, staging, and production environments
- 🔒 **Security-First Design**: Security groups, network isolation, and best practices
- 🚀 **Automated Deployment**: GitHub Actions workflows for CI/CD
- ✅ **Safety Mechanisms**: Multiple confirmation prompts for production changes
- 🔄 **Rollback Capability**: Easy rollback procedures in case of issues
- 📋 **Comprehensive Documentation**: Detailed deployment and operational guides

## Environment Strategy

| Environment | Purpose | CIDR | Approval Required |
|-------------|---------|------|-------------------|
| Development | Testing and experimentation | 10.0.0.0/16 | No |
| Staging | Pre-production validation | 10.1.0.0/16 | Recommended |
| Production | Live infrastructure | 10.2.0.0/16 | **Yes** |

## Quick Start

### Prerequisites

- Terraform >= 1.0
- AWS CLI configured
- Appropriate AWS permissions

### Deploy to Development

```bash
# Plan infrastructure changes
./scripts/deploy.sh dev plan

# Apply changes
./scripts/deploy.sh dev apply
```

### Deploy to Staging

```bash
./scripts/deploy.sh staging plan
./scripts/deploy.sh staging apply
```

### Deploy to Production

```bash
# Requires multiple confirmations
./scripts/deploy.sh production plan
./scripts/deploy.sh production apply
```

## Repository Structure

```
.
├── terraform/
│   ├── modules/
│   │   ├── network/      # VPC, subnets, routing
│   │   └── security/     # Security groups, NACLs
│   └── environments/
│       ├── dev/          # Development environment
│       ├── staging/      # Staging environment
│       └── production/   # Production environment
├── scripts/
│   ├── deploy.sh         # Deployment script with safety checks
│   └── rollback.sh       # Rollback script
├── docs/
│   └── DEPLOYMENT.md     # Comprehensive deployment guide
└── .github/
    └── workflows/
        ├── terraform-validate.yml  # Validation and testing
        └── deploy.yml              # Deployment workflow
```

## Documentation

- 📖 [Deployment Guide](docs/DEPLOYMENT.md) - Detailed deployment procedures and best practices
- 🔧 [Terraform Modules](terraform/modules/) - Reusable infrastructure modules
- 🔐 [Security Considerations](docs/DEPLOYMENT.md#security-considerations) - Security best practices

## Deployment Process

To avoid disruptions, always follow this flow:

```
Development → Staging → Production
```

1. **Develop and test** in the dev environment
2. **Validate** in the staging environment
3. **Deploy** to production only after staging validation

See the [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

## Safety Features

### 1. Multi-Level Confirmation
- Production deployments require explicit confirmation
- Destroy operations require typed confirmation

### 2. Automated Validation
- Terraform syntax validation
- Security scanning with tfsec
- Linting with tflint
- Format checking

### 3. State Management
- Automatic state backups
- Rollback capability
- State locking to prevent conflicts

### 4. Environment Isolation
- Separate VPCs per environment
- Independent security groups
- Isolated networking

## Contributing

1. Make changes in a feature branch
2. Test in dev environment first
3. Validate in staging
4. Create a pull request
5. After approval, deploy to production

## Rollback

If issues occur:

```bash
./scripts/rollback.sh <environment>
```

See [Rollback Procedures](docs/DEPLOYMENT.md#rollback-procedures) for details.
## VPN Management System

A robust YAML-based VPN management solution with monitoring, auto-reconnection, and health checking capabilities designed specifically for Starlink infrastructure security.

### Features

- **YAML-Based Configuration**: Easy-to-manage configuration file for all VPN settings
- **Multi-VPN Support**: Compatible with OpenVPN and WireGuard
- **Status Monitoring**: Real-time VPN connection status checks
- **Auto-Reconnection**: Automatic reconnection attempts on disconnection with configurable retry logic
- **Health Checking**: Validates VPN connectivity by pinging test hosts
- **Logging**: Comprehensive logging to console and file
- **CLI Interface**: Command-line interface for easy management

### Installation

1. Clone the repository:
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

No external dependencies required - uses Python 3.7+ standard library only.

### Generate Security Report

```bash
python3 src/starlink_security.py --report
```

### Check Status

```bash
python3 src/starlink_security.py --status
```

### Run Tests

```bash
python3 tests/test_security.py
```

## Documentation

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for detailed documentation including:
- Architecture overview
- Component descriptions
- Event logging format
- Configuration options
- Development guidelines

## Security

- Zero security vulnerabilities (CodeQL verified)
- All events logged with proper exception handling
- Graceful shutdown on SIGTERM/SIGINT
- Falls back to local directories when system paths are inaccessible

## License

See LICENSE file for details.
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

### Required Variables

- `environment`: Environment name (dev, staging, or production)

### Optional Variables

- `aws_region`: AWS region for deployment (default: us-west-2)
- `owner`: Team or individual responsible for the infrastructure
- `cost_center`: Cost center for billing and tracking
- `enable_cross_region`: Enable cross-region configuration
- `enable_backup`: Enable AWS Backup for resources
- `enable_monitoring`: Enable enhanced monitoring

See [variables.tf](variables.tf) for all available configuration options.

## Remote State Setup

To enable remote state management with S3 and DynamoDB:

1. Follow the instructions in [backend.tf](backend.tf) to create the required AWS resources
2. Uncomment the backend configuration block
3. Run `terraform init -migrate-state`

## Provider Configuration

This project configures the following Terraform providers:

- **AWS Provider** (v5.x): Primary cloud infrastructure provider
  - Primary region provider for main resources
  - Secondary us-east-1 provider for CloudFront and global services
- **Random Provider** (v3.6.x): For generating unique identifiers
- **Null Provider** (v3.2.x): For provisioners and local execution
- **Time Provider** (v0.11.x): For time-based resources
- **TLS Provider** (v4.0.x): For certificate generation

## Default Tags

All AWS resources are automatically tagged with:

- `Project`: secure-it-infra-Starlink
- `ManagedBy`: Terraform
- `Environment`: Selected environment (dev/staging/production)
- `Owner`: Team or individual owner
- `CostCenter`: Cost center for billing

Additional custom tags can be added via the `additional_tags` variable.

## Security Considerations

- Store sensitive variables in AWS Secrets Manager or environment variables
- Use IAM roles with least privilege principles
- Enable MFA for AWS accounts
- Regularly rotate access credentials
- Enable AWS CloudTrail for audit logging
- Use encrypted S3 buckets for state storage
- Implement state locking to prevent concurrent modifications

## Contributing

1. Create a feature branch
2. Make your changes
3. Run `terraform fmt` to format code
4. Run `terraform validate` to validate configuration
5. Submit a pull request

## License

See [LICENSE](LICENSE) for details.

## Support

For issues and questions, please open an issue in the GitHub repository.
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

### Usage

#### Show Status
Display current system status including security level, connection type, and metrics:
```bash
python3 starlink_security.py --status
```

#### Generate Security Report
Generate a comprehensive JSON security report:
```bash
python3 starlink_security.py --report
```

#### Run with Configuration
Start with a custom configuration file:
```bash
python3 starlink_security.py --config config.example.json
```

#### Run as Daemon
Run the security foundation as a background daemon:
```bash
python3 starlink_security.py --daemon
```

### Connection Degradation Detection

The system automatically detects connection degradation based on the following thresholds:
- **Packet Loss**: > 10%
- **Latency**: > 200ms
- **Connection Stability**: < 50%

When degradation is detected on a Starlink-only connection, the system automatically activates failover to the best available backup connection.

### Backup Connection Priority

Backup connections are prioritized as follows (lower number = higher priority):
1. LTE Backup (Priority 1)
2. Cable Backup (Priority 2)
3. Satellite Backup (Priority 3)
### Configuration

The VPN manager uses a YAML configuration file located at `config/vpn_config.yaml`. You can customize:

- VPN connection details (type, config file path)
- Monitoring intervals and retry logic
- Health check settings
- Notification preferences
- Starlink-specific settings

Example configuration:
```yaml
vpn:
  enabled: true
  connection:
    name: "starlink-secure-vpn"
    type: "openvpn"
    config_file: "/etc/openvpn/client.conf"
  monitoring:
    check_interval: 30
    auto_reconnect: true
    max_reconnect_attempts: 5
    reconnect_delay: 10
```

See `config/vpn_config.yaml` for the full configuration schema.

### Usage

#### Command Line Interface

**Monitor VPN with auto-reconnection:**
```bash
python main.py monitor
```

**Check VPN status:**
```bash
python main.py status
```

**Connect to VPN:**
```bash
python main.py connect
```

**Disconnect from VPN:**
```bash
python main.py disconnect
```

**Use custom configuration file:**
```bash
python main.py --config /path/to/config.yaml monitor
```

#### Python API

```python
from vpn_manager import VPNManager

# Initialize manager
manager = VPNManager('config/vpn_config.yaml')

# Check status
status = manager.get_vpn_status()
print(f"Connected: {status['connected']}")
print(f"Healthy: {status['healthy']}")

# Connect to VPN
if manager.connect_vpn():
    print("Connected successfully")

# Start monitoring (blocking)
manager.monitor()
```

### Testing

Run the test suite:
```bash
pytest test_starlink_security.py -v
```

### Configuration

See `config.example.json` for an example configuration file.
python -m unittest discover tests
```

Run specific test:
```bash
python -m unittest tests.test_vpn_manager.TestVPNManager.test_load_config
```

### Prerequisites

- Python 3.7+
- OpenVPN or WireGuard installed (depending on your VPN type)
- Appropriate permissions to manage VPN connections (typically root/sudo)

### Architecture

```
secure-it-infra-Starlink/
├── config/
│   └── vpn_config.yaml          # VPN configuration
├── vpn_manager/
│   ├── __init__.py              # Package initialization
│   └── vpn_manager.py           # Core VPN management logic
├── tests/
│   └── test_vpn_manager.py      # Unit tests
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

### How It Works

1. **Configuration Loading**: Reads VPN settings from YAML file
2. **Status Monitoring**: Periodically checks VPN connection status
3. **Health Checking**: Validates connectivity by pinging test hosts
4. **Auto-Reconnection**: Attempts reconnection when VPN drops or becomes unhealthy
5. **Logging**: Records all events for troubleshooting

### Security Considerations

- Store VPN credentials securely (not in the YAML config)
- Use appropriate file permissions for config files (e.g., `chmod 600`)
- Run with minimal required permissions
- Enable logging for audit trails
- Regularly update VPN software

### Troubleshooting

**VPN won't connect:**
- Verify VPN config file path is correct
- Ensure VPN software (OpenVPN/WireGuard) is installed
- Check system permissions
- Review logs for detailed error messages

**Health checks failing:**
- Verify test hosts are reachable
- Check firewall rules
- Adjust timeout values in configuration

**Auto-reconnection not working:**
- Ensure `auto_reconnect` is set to `true` in config
- Check max retry attempts aren't exhausted
- Review logs for specific error messages

### Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Tests are included for new features
- Documentation is updated

### License

See LICENSE file for details.

### Support

For issues, questions, or contributions, please open an issue on GitHub.
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
# Clone the repository
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink

# No additional dependencies required (uses Python standard library)
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

### Basic Example

```python
import asyncio
from starlink_security import (
    StarlinkSecurityFoundation,
    PolicyEnforcer,
    IncidentResponder,
    VPNManager,
    BackupManager
)

async def main():
    # Initialize security foundation
    foundation = StarlinkSecurityFoundation()
    foundation.running = True
    
    # Create security components
    policy_enforcer = PolicyEnforcer(foundation)
    incident_responder = IncidentResponder(foundation)
    vpn_manager = VPNManager(foundation)
    backup_manager = BackupManager(foundation)
    
    # Initialize components
    policy_enforcer.initialize()
    incident_responder.initialize()
    vpn_manager.initialize()
    backup_manager.initialize()
    
    # Enforce security policies
    await policy_enforcer.enforce_security_level("normal")

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Demo

```bash
python starlink_security.py
```

## Configuration

The security foundation can be configured with custom settings:

```python
config = {
    'security': {
        'vpn_required': True,
        'encryption_level': 'high'
    },
    'enterprise': {
        'backup_connections': ['cellular_backup', 'satellite_backup']
    }
}

foundation = StarlinkSecurityFoundation(config=config)
```

## Security Levels

- **normal**: Standard security policies applied
- **high**: Enhanced monitoring and stricter policies
- **critical**: Maximum security, non-essential traffic blocked

## Logging

Security events and incidents are logged to the `logs/` directory:
- Incident responses: `logs/incident_response_YYYYMMDD.json`
- Application logs: Console output with timestamps

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure all security implementations follow best practices and include appropriate tests.
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

## Architecture

### Components

1. **SecurityManager**: Main orchestration class
   - Manages security modules
   - Processes event queue
   - Coordinates incident response

2. **PolicyEnforcer**: Applies security policies
   - Manages firewall rules
   - Configures authentication
   - Sets encryption requirements

3. **IncidentResponder**: Handles security incidents
   - Executes response actions
   - Notifies security teams
   - Collects forensic data

4. **SecurityEvent**: Data class for security events
   - Event type and severity
   - Source and timestamp
   - Description and metadata

## Testing

Run the test suite:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_security_manager.py
```

## Security Levels

- **Low**: Permissive firewall, basic authentication
- **Medium**: Moderate firewall, multi-factor authentication
- **High**: Strict firewall, required encryption
- **Critical**: Lockdown mode, biometric authentication

## Event Severity Levels

- **Critical**: Immediate incident response, system isolation
- **High**: Alert administrators, increase monitoring
- **Medium**: Log and schedule review
- **Low**: Basic logging
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

### StarlinkMonitor

Main monitoring class for Starlink infrastructure.

#### Methods

- `__init__()`: Initialize the monitor with default metrics
- `update_metrics(**kwargs)`: Update individual metrics and recalculate scores
- `get_status_report()`: Get a comprehensive status report of all metrics

#### Metrics

The `SecurityMetrics` dataclass contains:
- `security_score`: Overall security score (0-100)
- `connection_stability`: Connection stability score (0-100)
- `signal_quality`: Signal quality percentage
- `latency_ms`: Network latency in milliseconds
- `packet_loss_rate`: Packet loss rate percentage
- `uptime_percentage`: System uptime percentage
- `failed_auth_attempts`: Number of failed authentication attempts
- `encryption_strength`: Encryption strength percentage
- `last_updated`: Timestamp of last update
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

The system consists of three main monitoring modules:
1. **Metrics Updater**: Updates network metrics every 5 seconds
2. **Security Scanner**: Performs periodic security scans
3. **Alert Monitor**: Checks for anomalies and triggers warnings

## Requirements

- Python 3.7+
- No external dependencies (uses only Python standard library)
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
- Scans network for authorized and unauthorized devices
- Checks for open ports on critical systems (SSH, Telnet, HTTP, HTTPS, RDP, VNC)
- Triggers alerts for security concerns
- Performance tracking for scan operations

### Threat Detector
- Updates threat intelligence feeds with resilience
- Scans for known threats
- Analyzes system logs for security events (e.g., brute force attempts)
- Exponential backoff for failed feed updates
- Tracks feed health and consecutive failures

### Policy Enforcer
- Manages security policies for network access, encryption, and authentication
- Adjusts security posture based on security level (NORMAL, ELEVATED, HIGH, CRITICAL)
- Provides policy retrieval interface

### Performance Metrics

The system tracks:
- Event counts by type
- Average response times for operations
- Error counts by type
- Total uptime

Access metrics via:
```python
metrics = foundation.get_metrics()
```

### Structured Logging

All logs are output in JSON format for easy integration with SIEM systems:

```json
{
  "timestamp": "2026-01-15T00:00:00.000000+00:00",
  "level": "INFO",
  "message": "Unauthorized devices detected: 1",
  "event_type": "unauthorized_device_detected",
  "source": "network_monitor",
  "data": {"unauthorized_devices": ["192.168.1.100"]}
}
```

## Security Levels

- **NORMAL**: Standard security policies
- **ELEVATED**: Moderate restrictions (SSH and HTTPS only)
- **HIGH**: Increased security measures
- **CRITICAL**: Maximum restrictions (HTTPS only, non-essential traffic blocked)

## Configuration

The system uses a default configuration that can be customized:

```python
config = {
    'monitoring': {
        'network_scan_interval': 300,  # seconds
        'threat_check_interval': 60     # seconds
    },
    'security': {
        'threat_intelligence_feeds': [
            'https://example.com/threat-feed-1',
            'https://example.com/threat-feed-2'
        ]
    }
}

foundation = StarlinkSecurityFoundation(config)
```

## Compliance & Governance

The security controls implemented in this system can be mapped to:
- **CIS Controls**: Network monitoring, threat detection, policy enforcement
- **NIST Cybersecurity Framework**: Identify, Protect, Detect, Respond, Recover
- **ISO 27001**: Information security management controls

## Future Enhancements

Potential improvements include:
- Automatic credential/secret rotation
- Fuzzing tests for robustness validation
- Load testing for high-volume scenarios
- Automated compliance reporting
- Integration with additional SIEM platforms
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

For issues and questions:

- Apache Pulsar: https://pulsar.apache.org/community
- Armada: https://github.com/G-Research/armada
- Repository Issues: https://github.com/danielnovais-tech/secure-it-infra-Starlink/issues

## References

- [Apache Pulsar](https://pulsar.apache.org/)
- [Armada](https://github.com/G-Research/armada)
- [Kubernetes](https://kubernetes.io/)
- [Starlink](https://www.starlink.com/)
For issues, questions, or contributions, please open a GitHub issue.
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

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
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
