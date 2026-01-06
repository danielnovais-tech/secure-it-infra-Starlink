# Secure IT Infrastructure - Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

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
