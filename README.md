# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Starlink Connection Metrics Module

This module provides advanced functionality to monitor and calculate quality metrics for Starlink satellite internet connections based on packet loss and latency.

### Features

- **Connection Quality Scoring**: Calculate overall connection quality (0-100) based on configurable thresholds
- **Stability Scoring**: Advanced stability calculation that heavily penalizes packet loss (70% weight) and considers latency (30% weight)
- **Connection Status**: Get comprehensive status ("Excellent", "Good", "Fair", "Poor") based on quality and stability metrics
- **Input Validation**: Automatic validation of metrics to ensure data integrity
- **🆕 Configurable Thresholds**: Customize packet loss and latency thresholds for different environments (satellite, fiber, remote)
- **🆕 Dynamic Scaling**: Adjust latency ceiling and weights based on environment or SLA requirements
- **🆕 Historical Smoothing**: Sliding window averaging to reduce false positives from momentary spikes
- **🆕 Alert Integration**: Event-driven alerts when stability falls below configurable thresholds
- **🆕 Service Level Mapping**: Map technical metrics to business service levels (Stable, Degraded, Critical, Offline)

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
print(f"Service Level: {status['service_level']}")
```

#### Advanced Usage with Custom Thresholds

```python
from starlink_metrics import (
    ConnectionMetrics, 
    StarlinkConnectionQuality,
    QualityThresholds,
    StabilityThresholds
)

# Create metrics object
metrics = ConnectionMetrics(packet_loss=5.0, latency=150.0)

# Configure custom thresholds for your environment
quality_thresholds = QualityThresholds(
    packet_loss_threshold=10.0,  # More lenient for satellite
    latency_threshold=200.0
)

stability_thresholds = StabilityThresholds(
    max_latency=600.0,  # Higher ceiling for satellite
    packet_loss_weight=0.7,
    latency_weight=0.3
)

# Create quality calculator with custom thresholds
quality = StarlinkConnectionQuality(
    metrics,
    quality_thresholds=quality_thresholds,
    stability_thresholds=stability_thresholds
)

# Get individual scores
quality_score = quality.calculate_quality_score()
stability_score = quality.calculate_stability_score()

# Get comprehensive status
status = quality.get_connection_status()
```

#### Alert Integration

```python
from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    AlertThresholds
)

# Define alert callback
def alert_handler(level, data):
    """Handle connection alerts."""
    print(f"Alert [{level}]: Stability={data['stability']:.3f}")
    print(f"Service Level: {data['service_level']}")
    if level == "critical":
        # Trigger failover mechanism (implement your own logic)
        # initiate_failover()
        pass

# Create quality monitor with alerts
metrics = ConnectionMetrics(packet_loss=25.0, latency=380.0)
quality = StarlinkConnectionQuality(
    metrics,
    alert_callback=alert_handler,
    alert_thresholds=AlertThresholds(
        critical_stability=0.3,  # Alert when < 0.3
        degraded_stability=0.5   # Warn when < 0.5
    )
)

status = quality.get_connection_status()
# Alert will be triggered automatically if thresholds are exceeded
```

#### Historical Smoothing

```python
from starlink_metrics import ConnectionMetrics, StarlinkConnectionQuality

# Enable 10-point sliding window for smoothing
quality = StarlinkConnectionQuality(
    ConnectionMetrics(packet_loss=5.0, latency=100.0),
    history_window_size=10
)

# Collect metrics over time
for measurement in measurements:
    quality.metrics = ConnectionMetrics(**measurement)
    
    # Get smoothed stability (averaged over history window)
    smoothed = quality.calculate_stability_score(use_smoothing=True)
    
    # Or get raw current value
    current = quality.calculate_stability_score(use_smoothing=False)
```

### Enhanced Features

#### 1. Configurable Thresholds

Adapt the monitoring system to different environments and SLA requirements:

```python
from starlink_metrics import QualityThresholds, StabilityThresholds

# Lenient thresholds for remote/satellite environments
lenient_quality = QualityThresholds(
    packet_loss_threshold=10.0,  # Allow up to 10% loss
    latency_threshold=250.0      # Allow up to 250ms latency
)

# Strict thresholds for critical applications
strict_quality = QualityThresholds(
    packet_loss_threshold=2.0,   # Low tolerance
    packet_loss_penalty=20.0,    # Heavy penalty
    latency_threshold=100.0,     # Low latency required
    latency_penalty=10.0
)
```

#### 2. Dynamic Scaling

Normalize latency expectations based on environment:

```python
# Satellite environment: higher latency tolerance
satellite_stability = StabilityThresholds(
    max_latency=800.0,           # Higher ceiling
    packet_loss_weight=0.8,      # Emphasize packet loss
    latency_weight=0.2
)

# Fiber environment: lower latency expectations
fiber_stability = StabilityThresholds(
    max_latency=100.0,           # Low ceiling
    packet_loss_weight=0.6,
    latency_weight=0.4           # Latency more important
)
```

#### 3. Service Level Mapping

Map technical metrics to business service levels:

- **STABLE**: Stability ≥ 0.7 (Production-ready)
- **DEGRADED**: Stability ≥ 0.5 (Reduced performance)
- **CRITICAL**: Stability ≥ 0.3 (Service at risk)
- **OFFLINE**: Stability < 0.3 (Service unavailable)

```python
status = quality.get_connection_status()
service_level = status['service_level']  # Returns: "Stable", "Degraded", "Critical", or "Offline"
```

#### 4. Historical Smoothing

Reduce false positives from momentary spikes:

```python
# Without smoothing: sensitive to individual measurements
# With smoothing: averaged over sliding window

quality = StarlinkConnectionQuality(
    metrics,
    history_window_size=10  # Average last 10 measurements
)
```

Benefits:
- Prevents false alarms from temporary fluctuations
- Provides more stable trend analysis
- Improves decision-making for automated systems

#### 5. Alert Integration

Facilitate proactive monitoring and failover:

```python
def alert_handler(level, data):
    """Example alert handler - implement your own logic."""
    if level == "critical":
        # trigger_failover()  # Implement your failover logic
        # send_notification("Critical: Connection failing")
        print(f"CRITICAL: Connection failing - {data}")
    elif level == "degraded":
        # send_notification("Warning: Connection degraded")
        print(f"WARNING: Connection degraded - {data}")
        
quality = StarlinkConnectionQuality(
    metrics,
    alert_callback=alert_handler
)
```

### Metrics Explanation

#### Quality Score (0-100)

The quality score starts at 100 and applies configurable penalties:
- **Default: Packet Loss > 5%**: -10 points
- **Default: Latency > 150ms**: -5 points

Thresholds and penalties can be customized via `QualityThresholds`.

#### Stability Score (0.0-1.0)

The stability score uses a weighted calculation with configurable parameters:
- **Packet Loss Factor** (default 70% weight): `max(0, 1 - packet_loss * multiplier)`
- **Latency Factor** (default 30% weight): `max(0, 1 - latency / max_latency)`

Default formula: `stability = loss_factor * 0.7 + latency_factor * 0.3`

This heavily penalizes packet loss while considering latency (default 500ms threshold).
All parameters can be customized via `StabilityThresholds`.

#### Connection Status (Legacy)

Status is determined based on both quality and stability scores:
- **Excellent**: Quality ≥ 90 AND Stability ≥ 0.9
- **Good**: Quality ≥ 75 AND Stability ≥ 0.7
- **Fair**: Quality ≥ 50 AND Stability ≥ 0.5
- **Poor**: Below Fair thresholds

#### Service Level (Governance)

Service level classification for aligning with business expectations:
- **Stable**: Stability ≥ 0.7 (configurable via `AlertThresholds.stable_stability`)
- **Degraded**: Stability ≥ 0.5 (configurable via `AlertThresholds.degraded_stability`)
- **Critical**: Stability ≥ 0.3 (configurable via `AlertThresholds.critical_stability`)
- **Offline**: Stability < 0.3

### Running Tests

```bash
# Run all tests (40 tests total)
pytest test_starlink_metrics.py test_enhanced_features.py -v

# Run basic tests only
pytest test_starlink_metrics.py -v

# Run enhanced feature tests only
pytest test_enhanced_features.py -v

# Run with coverage
pytest --cov=starlink_metrics --cov-report=html
```

### Examples

See comprehensive examples demonstrating all features:

```bash
# Basic usage examples
python3 example_usage.py

# Enhanced features demonstration
python3 enhanced_examples.py
```

### API Reference

#### `ConnectionMetrics`

Data class for storing connection metrics.

**Attributes:**
- `packet_loss` (float): Packet loss percentage (0-100)
- `latency` (float): Latency in milliseconds (≥ 0)

#### `QualityThresholds`

Configuration for quality score calculation.

**Attributes:**
- `packet_loss_threshold` (float): Packet loss % threshold (default: 5.0)
- `packet_loss_penalty` (float): Points to deduct (default: 10.0)
- `latency_threshold` (float): Latency ms threshold (default: 150.0)
- `latency_penalty` (float): Points to deduct (default: 5.0)

#### `StabilityThresholds`

Configuration for stability score calculation.

**Attributes:**
- `max_latency` (float): Latency ceiling in ms (default: 500.0)
- `packet_loss_weight` (float): Weight for packet loss factor (default: 0.7)
- `latency_weight` (float): Weight for latency factor (default: 0.3)
- `packet_loss_multiplier` (float): Multiplier for packet loss penalty (default: 2.0)

#### `AlertThresholds`

Configuration for alert triggering.

**Attributes:**
- `critical_stability` (float): Critical alert threshold (default: 0.3)
- `degraded_stability` (float): Degraded alert threshold (default: 0.5)
- `stable_stability` (float): Stable threshold (default: 0.7)

#### `ServiceLevel`

Enum for service level classification.

**Values:**
- `STABLE`: Production-ready connection
- `DEGRADED`: Reduced performance
- `CRITICAL`: Service at risk
- `OFFLINE`: Service unavailable

#### `StarlinkConnectionQuality`

Class for calculating connection quality and stability with advanced features.

**Constructor Parameters:**
- `metrics` (ConnectionMetrics): Current connection metrics
- `quality_thresholds` (QualityThresholds, optional): Custom quality thresholds
- `stability_thresholds` (StabilityThresholds, optional): Custom stability thresholds
- `alert_thresholds` (AlertThresholds, optional): Custom alert thresholds
- `alert_callback` (Callable, optional): Callback function for alerts `(level: str, data: dict) -> None`
- `history_window_size` (int, optional): Size of sliding window for smoothing (0 = disabled)

**Methods:**
- `calculate_quality_score()`: Returns quality score (0-100)
- `calculate_stability_score(use_smoothing=True)`: Returns stability score (0.0-1.0)
- `get_service_level(stability)`: Returns ServiceLevel enum
- `check_and_alert(stability)`: Check thresholds and trigger alerts
- `get_connection_status()`: Returns dict with comprehensive status

**Status Dictionary Keys:**
- `status`: Legacy status string ("Excellent", "Good", "Fair", "Poor")
- `quality_score`: Quality score (0-100)
- `stability_score`: Stability score (0.0-1.0)
- `service_level`: Service level string ("Stable", "Degraded", "Critical", "Offline")
- `packet_loss`: Current packet loss %
- `latency`: Current latency ms
- `alert_level` (optional): Alert level if triggered ("critical", "degraded")
- `stability_history_size` (optional): Number of historical measurements

#### `monitor_connection(packet_loss, latency)`

Convenience function to quickly monitor connection.

**Parameters:**
- `packet_loss` (float): Packet loss percentage (0-100)
- `latency` (float): Latency in milliseconds

**Returns:** Dictionary with connection status information

### License

Apache License 2.0 - See LICENSE file for details.

