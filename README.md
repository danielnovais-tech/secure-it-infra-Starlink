# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Overview

This repository provides a comprehensive security monitoring solution for Starlink infrastructure, featuring real-time metric tracking, anomaly detection, and security scoring.

## Features

- **Real-time Security Monitoring**: Track security metrics in real-time
- **Significant Change Logging**: Automatically logs changes in metrics that exceed configurable thresholds
- **Anomaly Detection**: Detects and flags security anomalies based on predefined rules
- **Security Scoring**: Calculates an overall security score (0-100) based on current metrics
- **Flexible Alerting**: Supports severity-based filtering of security events

## Installation

```bash
# Clone the repository
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
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

