# Quick Start Guide - Secure IT Starlink

## Installation

```bash
# Clone the repository
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Basic Usage

### 1. Run with Default Configuration

```bash
secure-it-starlink
```

### 2. Run with Custom Configuration

```bash
secure-it-starlink -c configs/production_config.yaml
```

### 3. Check System Status

```bash
secure-it-starlink --status
```

## Quick Examples

### Configuration Management

```python
from secure_it_starlink.config import ConfigurationManager

# Load and merge configurations
config = ConfigurationManager()
config.load_and_merge('configs/production_config.yaml')

# Access configuration values
security_weight = config.get('metrics.security.weight')
log_level = config.get('logging.structured.level')
```

### Metrics Collection

```python
from secure_it_starlink.metrics import MetricsCollector

# Initialize collector
collector = MetricsCollector(config.get('metrics'))

# Collect metrics
metrics = collector.collect_metrics(
    security_data={
        'firewall_status': 95.0,
        'encryption_level': 90.0
    },
    connection_data={
        'uptime_percentage': 99.8,
        'latency': 25.0
    },
    performance_data={
        'cpu_usage': 45.0,
        'memory_usage': 60.0
    }
)

print(f"Composite Score: {metrics['composite_score']}")
```

### Automated Responses

```python
from secure_it_starlink.automated_responses import AutomatedResponseCoordinator

# Initialize coordinator
coordinator = AutomatedResponseCoordinator(config.get('automated_responses'))

# Process security event
event = {
    'type': 'security_threat',
    'severity': 'high',
    'device_id': 'device-001',
    'source_ip': '192.168.1.100',
    'reason': 'Malware detected'
}

actions = coordinator.process_event(event)
print(f"Triggered {len(actions)} automated actions")
```

### Structured Logging

```python
from secure_it_starlink.logging import StructuredLogger

# Initialize logger
logger = StructuredLogger(config.get('logging'))

# Log with structured data
logger.info("Security event detected", 
           event_type='intrusion_attempt',
           source_ip='192.168.1.100',
           severity='high')

# Check correlated events
incidents = logger.get_correlated_events(3600)
```

## Running Tests

```bash
# Run functionality tests
python3 tests/test_functionality.py

# Run usage examples
python3 examples/usage_examples.py
```

## Configuration Files

- `configs/default_config.yaml` - Default configuration with all settings
- `configs/development_config.yaml` - Development environment overrides
- `configs/production_config.yaml` - Production environment overrides

## Key Features

1. **Comprehensive Metrics**
   - Security scoring (0-100)
   - Connection stability monitoring
   - Performance tracking

2. **Automated Responses**
   - Threat containment (device isolation, IP blocking)
   - Policy enforcement (bandwidth limits, access control)
   - Failover activation (backup link switching)

3. **Detailed Logging**
   - JSON-structured logs
   - Event correlation
   - Pattern detection (brute force, data exfiltration)

4. **Configuration Management**
   - YAML-based configuration
   - Deep merging support
   - Environment-specific overrides

## Next Steps

1. Review the comprehensive [README.md](README.md) for detailed documentation
2. Explore [examples/usage_examples.py](examples/usage_examples.py) for more examples
3. Customize configuration files for your environment
4. Integrate with your existing monitoring infrastructure

## Support

For issues or questions, please open an issue on GitHub.
