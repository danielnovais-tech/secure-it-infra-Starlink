# Starlink Security Foundation

Enterprise security management system for infrastructures using Starlink connectivity.

## Overview

The Starlink Security Foundation provides comprehensive security monitoring, event logging, and network management capabilities for enterprise infrastructures relying on Starlink connectivity, particularly in remote or rural settings.

## Features

- **Security Event Logging**: Automatic logging of security events to monthly JSON files
- **Network Monitoring**: Continuous monitoring of network devices and open ports
- **Metrics Tracking**: Real-time tracking of latency, jitter, packet loss, and throughput
- **Security Scoring**: Automated calculation of security scores and connection stability
- **Recommendations**: Intelligent security recommendations based on current metrics
- **Threat Management**: Active threat tracking and management
- **Signal Handling**: Graceful shutdown on SIGTERM and SIGINT signals

## Installation

```bash
# Clone the repository
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink

# The application uses only Python standard library
# Python 3.7+ required
```

## Usage

### Generate Security Report

```bash
python3 src/starlink_security.py --report
```

Example output:
```json
{
  "timestamp": "2026-01-07T00:00:00.000000",
  "security_level": "normal",
  "connection_type": "starlink_only",
  "metrics": {
    "latency_ms": 0.0,
    "jitter_ms": 0.0,
    "packet_loss_percent": 0.0,
    "throughput_mbps": 0.0,
    "security_score": 100.0,
    "connection_stability": 100.0
  },
  "active_threats": [],
  "modules_status": {},
  "recommendations": []
}
```

### Check Status

```bash
python3 src/starlink_security.py --status
```

### Run with Custom Configuration

```bash
python3 src/starlink_security.py --config /path/to/config.yaml
```

## Architecture

### Core Components

- **StarlinkSecurityFoundation**: Main orchestrator managing security operations
- **NetworkMonitor**: Monitors network devices and open ports
- **SecurityEvent**: Data structure for security events
- **NetworkMetrics**: Container for network performance metrics

### Security Levels

- `NORMAL`: Standard security posture
- `ELEVATED`: Increased monitoring and restrictions
- `CRITICAL`: Maximum security measures active
- `RECOVERY`: System in recovery mode

### Connection Types

- `STARLINK_ONLY`: Using Starlink exclusively
- `HYBRID`: Starlink + backup connection
- `FAILOVER`: Primary connection failed, using Starlink

## Event Logging

Security events are automatically logged to JSON files in `/var/log/starlink-security/` organized by month (e.g., `events_202601.json`).

Each event includes:
- Timestamp
- Event type
- Severity level
- Source
- Description
- Metadata

Example log entry:
```json
{
  "timestamp": "2026-01-07T00:33:12.160000",
  "event_type": "unauthorized_device_detected",
  "severity": "warning",
  "source": "network_monitor",
  "description": "Unauthorized devices detected: 3",
  "metadata": {
    "unauthorized_devices": ["device_16", "device_17", "device_18"]
  }
}
```

## Testing

Run the test suite:

```bash
python3 tests/test_security.py
```

Tests cover:
- Foundation initialization
- Security report generation
- Event triggering and logging
- Recommendations generation
- Network monitor initialization

## Directory Structure

```
/etc/starlink-security/    # Configuration files
/var/lib/starlink-security/ # Application data
/var/log/starlink-security/ # Log files
```

## Configuration

Default configuration includes:

- **Security Settings**:
  - Encryption enabled
  - VPN required
  - Minimum TLS version: 1.3

- **Monitoring Intervals**:
  - Network scan: 300 seconds
  - Threat check: 60 seconds
  - Log retention: 90 days

- **Starlink Settings**:
  - Gateway IP: 192.168.100.1
  - Performance thresholds for latency, jitter, packet loss, and throughput

## Development

### Project Structure

```
secure-it-infra-Starlink/
├── src/
│   └── starlink_security.py   # Main application
├── tests/
│   └── test_security.py       # Test suite
├── README.md                   # This file
└── IMPLEMENTATION.md           # Implementation details
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

See LICENSE file for details.

## Security Considerations

- Events are logged locally - ensure log directory has appropriate permissions
- Signal handlers ensure graceful shutdown
- Network scanning is simulated in this version - production deployments should use proper tools (scapy, nmap)
- Port scanning is limited to localhost in this implementation

## Roadmap

Future enhancements may include:
- Remote logging capabilities
- Integration with SIEM systems
- Real-time alerting via email/SMS
- Dashboard UI
- Extended threat intelligence integration
- Automated response actions
