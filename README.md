# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

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

