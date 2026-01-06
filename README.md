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
