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

# Or initialize with a custom configuration file
foundation = StarlinkSecurityFoundation(config_path="/path/to/config.json")

# Log a security event
event = SecurityEvent(
    timestamp=datetime.now(),
    event_type="connection_attempt",
    severity="medium",
    source="firewall",
    description="Unauthorized connection attempt detected"
)
foundation.log_event(event)

# Add event to the queue for processing
foundation.events_queue.put(event)

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

# Track active threats
foundation.active_threats.add("port_scan_192.168.1.100")

# Check security modules status
print(foundation.security_modules)

# Get unresolved events
unresolved = foundation.get_unresolved_events()
```

### Configuration File Example

Create a JSON configuration file:

```json
{
    "security_level": "elevated",
    "connection_type": "hybrid",
    "monitoring_interval": 30,
    "max_events_queue": 2000,
    "encryption_enabled": true,
    "custom_settings": {
        "alert_threshold": 5,
        "auto_response": true
    }
}
```

Then load it:

```python
foundation = StarlinkSecurityFoundation(config_path="config.json")
print(foundation.config)
```

## Directory Structure

The module automatically creates the following directories in your home directory:

- `~/.starlink_security/config` - Configuration files and encryption keys
- `~/.starlink_security/data` - Data storage
- `~/.starlink_security/logs` - Log files

### Encryption

The module automatically generates and stores an encryption key on first use at:
- `~/.starlink_security/config/encryption.key`

This key persists across instances and is used for secure communications.

## API Reference

### Classes

#### `StarlinkSecurityFoundation`
Main class for security operations.

**Initialization:**
- `__init__(config_path: Optional[str] = None)` - Initialize with optional configuration file

**Attributes:**
- `config: Dict[str, Any]` - Configuration dictionary
- `security_level: SecurityLevel` - Current security level
- `connection_type: ConnectionType` - Current connection type
- `encryption_key: bytes` - Encryption key for secure communications
- `running: bool` - Running status flag
- `events_queue: queue.Queue` - Queue for event processing
- `metrics: NetworkMetrics` - Current network metrics
- `active_threats: Set[str]` - Set of active threat identifiers
- `security_modules: Dict[str, Any]` - Security modules and their status
- `events: List[SecurityEvent]` - List of logged events

**Methods:**
- `log_event(event: SecurityEvent)` - Log a security event
- `update_metrics(metrics: NetworkMetrics)` - Update network metrics
- `set_security_level(level: SecurityLevel)` - Change security level
- `get_unresolved_events()` - Get unresolved security events

**Private Methods:**
- `_load_config(config_path)` - Load configuration from file
- `_initialize_encryption()` - Initialize encryption key
- `_initialize_modules()` - Initialize security modules

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
- cryptography>=42.0.4

Install dependencies:
```bash
pip install -r requirements.txt
```

## License

See the LICENSE file for details.
