# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Overview

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

## License

See LICENSE file for details.
