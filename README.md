# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Starlink Connection Metrics Module

This module provides functionality to monitor and calculate quality metrics for Starlink satellite internet connections based on packet loss and latency.

### Features

- **Connection Quality Scoring**: Calculate overall connection quality (0-100) based on configurable thresholds
- **Stability Scoring**: Advanced stability calculation that heavily penalizes packet loss (70% weight) and considers latency (30% weight)
- **Connection Status**: Get comprehensive status ("Excellent", "Good", "Fair", "Poor") based on quality and stability metrics
- **Input Validation**: Automatic validation of metrics to ensure data integrity

### Installation

```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

### Usage

#### Quick Start

```python
from starlink_metrics import monitor_connection

# Monitor connection with current metrics
status = monitor_connection(packet_loss=3.0, latency=120.0)
print(f"Connection Status: {status['status']}")
print(f"Quality Score: {status['quality_score']}/100")
print(f"Stability Score: {status['stability_score']:.3f}")
```

#### Advanced Usage

```python
from starlink_metrics import ConnectionMetrics, StarlinkConnectionQuality

# Create metrics object
metrics = ConnectionMetrics(packet_loss=5.0, latency=150.0)

# Create quality calculator
quality = StarlinkConnectionQuality(metrics)

# Get individual scores
quality_score = quality.calculate_quality_score()
stability_score = quality.calculate_stability_score()

# Get comprehensive status
status = quality.get_connection_status()
```

### Metrics Explanation

#### Quality Score (0-100)

The quality score starts at 100 and applies penalties based on:
- **Packet Loss > 5%**: -10 points
- **Latency > 150ms**: -5 points

The score is clamped between 0 and 100.

#### Stability Score (0.0-1.0)

The stability score uses a weighted calculation:
- **Packet Loss Factor** (70% weight): `max(0, 1 - packet_loss * 2)`
- **Latency Factor** (30% weight): `max(0, 1 - latency / 500)`

Formula: `stability = loss_factor * 0.7 + latency_factor * 0.3`

This heavily penalizes packet loss while still considering latency with a 500ms threshold.

#### Connection Status

Status is determined based on both quality and stability scores:
- **Excellent**: Quality ≥ 90 AND Stability ≥ 0.9
- **Good**: Quality ≥ 75 AND Stability ≥ 0.7
- **Fair**: Quality ≥ 50 AND Stability ≥ 0.5
- **Poor**: Below Fair thresholds

### Running Tests

```bash
# Run all tests
pytest test_starlink_metrics.py -v

# Run with coverage
pytest test_starlink_metrics.py --cov=starlink_metrics
```

### Examples

See `example_usage.py` for comprehensive examples:

```bash
python3 example_usage.py
```

### API Reference

#### `ConnectionMetrics`

Data class for storing connection metrics.

**Attributes:**
- `packet_loss` (float): Packet loss percentage (0-100)
- `latency` (float): Latency in milliseconds (≥ 0)

#### `StarlinkConnectionQuality`

Class for calculating connection quality and stability.

**Methods:**
- `calculate_quality_score()`: Returns quality score (0-100)
- `calculate_stability_score()`: Returns stability score (0.0-1.0)
- `get_connection_status()`: Returns dictionary with comprehensive status

#### `monitor_connection(packet_loss, latency)`

Convenience function to quickly monitor connection.

**Parameters:**
- `packet_loss` (float): Packet loss percentage (0-100)
- `latency` (float): Latency in milliseconds

**Returns:** Dictionary with connection status information

### License

Apache License 2.0 - See LICENSE file for details.

