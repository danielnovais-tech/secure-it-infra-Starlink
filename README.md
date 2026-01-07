# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Features

This system provides comprehensive network monitoring and security management for Starlink connections:

### Network Stability Monitoring
- Calculates network stability score (0-100) based on performance metrics
- Deducts points for high jitter (up to 30 points)
- Deducts points for high packet loss (up to 40 points)
- Ensures stability scores remain within valid bounds (0-100)

### Anomaly Detection
- Monitors latency, jitter, packet loss, and throughput
- Triggers alerts when metrics exceed configured thresholds
- Provides detailed anomaly information in event data

### Security Level Management
- Tracks overall security score
- Automatically adjusts security level (NORMAL, ELEVATED, CRITICAL)
- Triggers events when security level changes
- Thresholds:
  - CRITICAL: security_score < 50
  - ELEVATED: 50 ≤ security_score < 70
  - NORMAL: security_score ≥ 70

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

## Configuration

See `config.example.json` for a sample configuration file.

### Performance Thresholds

- `max_latency`: Maximum acceptable latency in milliseconds
- `max_jitter`: Maximum acceptable jitter in milliseconds
- `max_packet_loss`: Maximum acceptable packet loss percentage
- `min_throughput`: Minimum acceptable throughput in Mbps
