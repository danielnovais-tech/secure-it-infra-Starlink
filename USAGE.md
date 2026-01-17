# Starlink Security Foundation

A Python module for securing enterprise infrastructures using Starlink connectivity, providing monitoring, enforcement, and response capabilities with enterprise-grade features.

## Features

- **Automatic Directory Setup**: Creates necessary configuration, data, and log directories
- **Structured JSON Logging**: Comprehensive logging with both console and file outputs in JSON format
- **Configuration Validation**: Schema validation for robust configuration management
- **Thread Safety**: Full concurrent access support with locks for multi-threaded environments
- **Lifecycle Management**: Explicit start() and stop() methods for clean module initialization and shutdown
- **Metrics & Monitoring**: Exposed counters for observability (active threats, queue size, etc.)
- **Dependency Injection**: Module factory pattern for testing and swapping implementations
- **Security Hardening**: Encryption key rotation policies with automatic backup
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

### Basic Usage with Lifecycle Management

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

# Start the foundation (activates all modules)
foundation.start()

# Or initialize with a custom configuration file
foundation = StarlinkSecurityFoundation(config_path="/path/to/config.json")
foundation.start()

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

# Track active threats (thread-safe)
foundation.add_threat("port_scan_192.168.1.100")
foundation.remove_threat("port_scan_192.168.1.100")

# Get observability metrics
metrics_summary = foundation.get_metrics_summary()
print(f"Active threats: {metrics_summary['active_threats_count']}")
print(f"Queue utilization: {metrics_summary['events_queue_utilization']:.2f}%")
print(f"Key rotation needed: {metrics_summary['key_rotation_needed']}")

# Rotate encryption key when needed
if foundation._needs_key_rotation():
    foundation.rotate_encryption_key()

# Stop the foundation when done
foundation.stop()
```

### Configuration File Example

Create a JSON configuration file with extended options:

```json
{
    "security_level": "elevated",
    "connection_type": "hybrid",
    "monitoring_interval": 30,
    "max_events_queue": 2000,
    "encryption_enabled": true,
    "key_rotation_days": 90,
    "log_level": "DEBUG",
    "modules": {
        "firewall": {"enabled": true},
        "intrusion_detection": {"enabled": true},
        "threat_analysis": {"enabled": true}
    },
    "custom_settings": {
        "alert_threshold": 5,
        "auto_response": true
    }
}
```

Then load it:

```python
foundation = StarlinkSecurityFoundation(config_path="config.json")
foundation.start()
print(foundation.config)
```

### Dependency Injection for Testing

Use custom module implementations via dependency injection:

```python
from starlink_security import StarlinkSecurityFoundation, SecurityModule

class CustomFirewallModule(SecurityModule):
    def start(self):
        super().start()
        # Custom firewall logic
        self.status = "custom_active"
    
    def stop(self):
        # Custom cleanup
        super().stop()

def custom_module_factory(name, enabled):
    if name == "firewall":
        return CustomFirewallModule(name, enabled)
    return SecurityModule(name, enabled)

foundation = StarlinkSecurityFoundation(module_factory=custom_module_factory)
foundation.start()
```

### Thread-Safe Operations

All operations are thread-safe for concurrent environments:

```python
import threading

def process_threats(foundation):
    for i in range(100):
        foundation.add_threat(f"threat_{i}")
        # Process...
        foundation.remove_threat(f"threat_{i}")

# Run in multiple threads
threads = [threading.Thread(target=process_threats, args=(foundation,)) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Directory Structure

The module automatically creates the following directories in your home directory:

- `~/.starlink_security/config` - Configuration files and encryption keys
- `~/.starlink_security/data` - Data storage
- `~/.starlink_security/logs` - Structured JSON log files (daily rotation)

### Logging

The module provides structured logging with both console and file outputs:

- **Console logging**: Human-readable format at INFO level
- **File logging**: JSON format at DEBUG level in `~/.starlink_security/logs/starlink_security_YYYYMMDD.log`

Example log entry:

```json
{
    "timestamp": "2026-01-15T22:12:16.728000",
    "level": "INFO",
    "module": "starlink_security",
    "function": "__init__",
    "message": "Starlink Security Foundation initialized successfully"
}
```

### Encryption

The module automatically generates and stores an encryption key on first use at:

- `~/.starlink_security/config/encryption.key`

This key persists across instances and is used for secure communications. The module supports automatic key rotation:

```python
# Check if rotation is needed (default: 90 days)
if foundation._needs_key_rotation():
    foundation.rotate_encryption_key()
```

Key backups are created at:

- `~/.starlink_security/config/encryption.key.backup.YYYYMMDDHHMMSS`

## API Reference

### Classes

#### `StarlinkSecurityFoundation`

Main class for security operations with lifecycle management.

**Initialization:**

- `__init__(config_path: Optional[str] = None, module_factory: Optional[Callable] = None)` - Initialize with optional configuration file and module factory for dependency injection

**Attributes:**

- `config: Dict[str, Any]` - Validated configuration dictionary
- `security_level: SecurityLevel` - Current security level
- `connection_type: ConnectionType` - Current connection type
- `encryption_key: bytes` - Encryption key for secure communications
- `running: bool` - Running status flag (controlled by start/stop)
- `events_queue: queue.Queue` - Thread-safe queue for event processing (with maxsize)
- `metrics: NetworkMetrics` - Current network metrics (thread-safe access)
- `active_threats: Set[str]` - Set of active threat identifiers (thread-safe)
- `security_modules: Dict[str, SecurityModule]` - Security modules with lifecycle management
- `events: List[SecurityEvent]` - List of logged events (thread-safe)
- `logger: logging.Logger` - Structured logger instance

**Lifecycle Methods:**

- `start()` - Start all security modules and begin operations
- `stop()` - Stop all security modules and cease operations

**Core Methods:**

- `log_event(event: SecurityEvent)` - Log a security event (thread-safe)
- `update_metrics(metrics: NetworkMetrics)` - Update network metrics (thread-safe)
- `set_security_level(level: SecurityLevel)` - Change security level
- `add_threat(threat_id: str)` - Add an active threat (thread-safe)
- `remove_threat(threat_id: str)` - Remove an active threat (thread-safe)
- `get_unresolved_events()` - Get unresolved security events (thread-safe)

**Monitoring & Observability:**

- `get_metrics_summary()` - Get comprehensive metrics for monitoring/observability
  - Returns: active_threats_count, unresolved_events_count, queue_utilization, network_metrics, module status, key age, etc.

**Security Methods:**

- `rotate_encryption_key()` - Rotate encryption key with automatic backup
- `_needs_key_rotation()` - Check if key rotation is needed based on age

**Private Methods:**

- `_load_config(config_path)` - Load and validate configuration from file
- `_initialize_encryption()` - Initialize encryption key with age tracking
- `_initialize_modules()` - Initialize security modules via factory pattern
- `_default_module_factory(name, enabled)` - Default module factory

#### `SecurityModule`

Base class for security modules with lifecycle management.

**Methods:**

- `start()` - Start the module
- `stop()` - Stop the module
- `get_status()` - Get module status dictionary

**Attributes:**

- `name: str` - Module name
- `enabled: bool` - Whether module is enabled
- `status: str` - Current status (initialized, active, stopped)
- `logger: logging.Logger` - Module-specific logger

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
