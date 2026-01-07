# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Starlink Enterprise Security Foundation

A comprehensive security management system for Starlink enterprise connections with automatic failover, monitoring, and threat detection capabilities.

### Features

- **Connection Monitoring**: Continuous monitoring of connection metrics including packet loss, latency, and stability
- **Automatic Failover**: Intelligent failover to backup connections when primary connection degrades
- **Security Metrics**: Real-time security scoring and threat tracking
- **Multiple Connection Types**: Support for Starlink-only, failover, dual-WAN, and load-balanced configurations
- **CLI Interface**: Command-line tools for status checking, reporting, and daemon mode
- **Event Logging**: Comprehensive logging of all security and connection events

### Installation

1. Clone the repository:
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

2. Install dependencies:
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

### Testing

Run the test suite:
```bash
pytest test_starlink_security.py -v
```

### Configuration

See `config.example.json` for an example configuration file.

### License

See LICENSE file for details.
