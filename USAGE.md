# Starlink Security Foundation

A Python module for securing enterprise infrastructures using Starlink connectivity, providing monitoring, enforcement, and response capabilities.

## Features

- **Automatic Directory Setup**: Creates necessary configuration, data, and log directories
- **Security Levels**: Support for NORMAL, ELEVATED, CRITICAL, and RECOVERY operational modes
- **Connection Types**: Handles STARLINK_ONLY, HYBRID, and FAILOVER connection configurations
- **Event Logging**: Track and manage security events with metadata
- **Network Metrics**: Monitor network performance and security scores

## Installation

Simply import the module in your Python code:

```python
from starlink_security import StarlinkSecurityFoundation
```

## Quick Start

### Basic Usage

```python
from datetime import datetime
from starlink_security import (
    StarlinkSecurityFoundation,
    SecurityLevel,
    ConnectionType,
    SecurityEvent,
    NetworkMetrics
)

# Initialize the security foundation
foundation = StarlinkSecurityFoundation()

# Log a security event
event = SecurityEvent(
    timestamp=datetime.now(),
    event_type="connection_attempt",
    severity="medium",
    source="firewall",
    description="Unauthorized connection attempt detected"
)
foundation.log_event(event)

# Update network metrics
metrics = NetworkMetrics(
    latency=25.5,
    jitter=2.1,
    packet_loss=0.1,
    throughput=100.0,
    security_score=95.0,
    connection_stability=98.0
)
foundation.update_metrics(metrics)

# Change security level
foundation.set_security_level(SecurityLevel.ELEVATED)

# Get unresolved events
unresolved = foundation.get_unresolved_events()
```

### Advanced Configuration

```python
# Initialize with custom settings
foundation = StarlinkSecurityFoundation(
    security_level=SecurityLevel.CRITICAL,
    connection_type=ConnectionType.HYBRID
)
```

## Directory Structure

The module automatically creates the following directories in your home directory:

- `~/.starlink_security/config` - Configuration files
- `~/.starlink_security/data` - Data storage
- `~/.starlink_security/logs` - Log files

## API Reference

### Classes

#### `StarlinkSecurityFoundation`
Main class for security operations.

**Methods:**
- `log_event(event: SecurityEvent)` - Log a security event
- `update_metrics(metrics: NetworkMetrics)` - Update network metrics
- `set_security_level(level: SecurityLevel)` - Change security level
- `get_unresolved_events()` - Get unresolved security events

#### `SecurityLevel` (Enum)
- `NORMAL` - Normal operations
- `ELEVATED` - Increased security monitoring
- `CRITICAL` - Maximum security protocols
- `RECOVERY` - System recovery mode

#### `ConnectionType` (Enum)
- `STARLINK_ONLY` - Starlink as sole connection
- `HYBRID` - Starlink + backup connection
- `FAILOVER` - Primary failed, using Starlink

#### `SecurityEvent` (Dataclass)
Security event data structure with fields:
- `timestamp: datetime` - When the event occurred
- `event_type: str` - Type of event
- `severity: str` - Event severity level
- `source: str` - Source of the event
- `description: str` - Event description
- `metadata: Dict[str, Any]` - Additional metadata
- `resolved: bool` - Resolution status

#### `NetworkMetrics` (Dataclass)
Network performance metrics with fields:
- `latency: float` - Network latency
- `jitter: float` - Network jitter
- `packet_loss: float` - Packet loss percentage
- `throughput: float` - Throughput in Mbps
- `security_score: float` - Security score (0-100)
- `connection_stability: float` - Connection stability (0-100)
- `last_outage: Optional[datetime]` - Last outage timestamp
- `threat_indicators: List[str]` - List of threat indicators

## Error Handling

The module handles directory creation errors gracefully:

```python
try:
    foundation = StarlinkSecurityFoundation()
except PermissionError as e:
    print(f"Permission denied: {e}")
except OSError as e:
    print(f"Filesystem error: {e}")
```

## Requirements

- Python 3.7+
- No external dependencies (uses standard library only)

## License

See the LICENSE file for details.
