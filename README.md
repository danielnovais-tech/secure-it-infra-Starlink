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

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Version

Current version: 1.0.0
