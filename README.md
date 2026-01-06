# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Overview

The **Secure IT Infrastructure for Starlink** provides a comprehensive core security foundation for managing enterprise infrastructures that use Starlink satellite connectivity. This package offers structured security management, connection type handling, event-driven architecture, and encryption capabilities.

## Features

### 🔒 Structured Security Levels

Four distinct security levels for granular control:

- **NORMAL**: Standard operational security level
- **ELEVATED**: Increased security monitoring and controls
- **CRITICAL**: Maximum security protocols activated
- **RECOVERY**: System recovery mode with restricted access

### 🌐 Connection Type Management

Support for different network connection modes:

- **STARLINK_ONLY**: Exclusive Starlink satellite connection
- **HYBRID**: Combined Starlink and terrestrial connection
- **FAILOVER**: Automatic failover between connection types

### 📡 Event-Driven Architecture

Robust event system with queued security events:

- Thread-safe event queue
- Multiple event types (security changes, connection status, intrusions, etc.)
- Event handlers with async support
- Event history with filtering capabilities

### 🔐 Encryption Management

Secure handling of sensitive data:

- Fernet symmetric encryption
- Password-based key derivation (PBKDF2HMAC)
- Key rotation support
- String and byte encryption

## Installation

```bash
pip install -e .
```

### Development Installation

```bash
pip install -r requirements-dev.txt
```

## Quick Start

```python
from secure_it_infra import (
    SecurityLevel,
    ConnectionType,
    SecurityEvent,
    SecurityEventQueue,
    EventType,
    EncryptionManager,
)

# Create a security event
event = SecurityEvent(
    event_type=EventType.SECURITY_LEVEL_CHANGE,
    security_level=SecurityLevel.ELEVATED,
    message="Security level elevated",
)

# Initialize event queue
queue = SecurityEventQueue()
queue.put(event)

# Encrypt sensitive data
manager = EncryptionManager.from_password("secure_password")
encrypted = manager.encrypt_str("sensitive data")
decrypted = manager.decrypt_str(encrypted)
```

## Usage Examples

### Security Levels

```python
from secure_it_infra import SecurityLevel

# Compare security levels
if SecurityLevel.CRITICAL.is_higher_than(SecurityLevel.ELEVATED):
    print("Critical security measures activated")

# Check priority
print(f"Priority: {SecurityLevel.RECOVERY.priority}")  # Output: 3
```

### Connection Types

```python
from secure_it_infra import ConnectionType

# Check connection capabilities
connection = ConnectionType.HYBRID
if connection.supports_redundancy:
    print("Redundancy available")

# Verify satellite-only mode
if ConnectionType.STARLINK_ONLY.is_satellite_only:
    print("Operating in satellite-only mode")
```

### Event Queue

```python
from secure_it_infra import SecurityEvent, SecurityEventQueue, EventType

# Create and manage events
queue = SecurityEventQueue()

event = SecurityEvent(
    event_type=EventType.INTRUSION_DETECTED,
    security_level=SecurityLevel.CRITICAL,
    source="firewall",
    message="Unauthorized access attempt",
    data={"ip": "192.168.1.100"},
)

queue.put(event)

# Process events
while not queue.is_empty():
    event = queue.get()
    print(f"Event: {event.message}")

# Filter event history
critical_events = queue.get_history(security_level=SecurityLevel.CRITICAL)
```

### Async Event Processing

```python
import asyncio
from secure_it_infra import SecurityEventQueue, EventType

async def main():
    queue = SecurityEventQueue()
    
    # Register event handler
    def handle_intrusion(event):
        print(f"⚠️  {event.message}")
    
    queue.register_handler(EventType.INTRUSION_DETECTED, handle_intrusion)
    
    # Start processing
    process_task = asyncio.create_task(queue.process_events())
    
    # Add events...
    # (events will be handled automatically)
    
    # Stop processing
    queue.stop_processing()
    await process_task

asyncio.run(main())
```

### Encryption

```python
from secure_it_infra import EncryptionManager

# Auto-generated key
manager = EncryptionManager()
encrypted = manager.encrypt_str("API Key: sk_live_123")
decrypted = manager.decrypt_str(encrypted)

# Password-based encryption
manager = EncryptionManager.from_password("my_password")
encrypted = manager.encrypt_str("secret data")

# Recreate manager with same password and salt
restored = EncryptionManager.from_password("my_password", salt=manager.salt)
decrypted = restored.decrypt_str(encrypted)

# Key rotation
old_key = manager.rotate_key()
```

## Running Examples

A comprehensive example demonstrating all features:

```bash
python examples/basic_usage.py
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=secure_it_infra --cov-report=html
```

## API Reference

### SecurityLevel

Enum with four security levels: `NORMAL`, `ELEVATED`, `CRITICAL`, `RECOVERY`

**Methods:**
- `is_higher_than(other)`: Compare security levels
- `is_lower_than(other)`: Compare security levels

**Properties:**
- `priority`: Numeric priority (0-3)

### ConnectionType

Enum with three connection types: `STARLINK_ONLY`, `HYBRID`, `FAILOVER`

**Properties:**
- `supports_redundancy`: Whether connection supports redundancy
- `is_satellite_only`: Whether connection is satellite-only

### SecurityEvent

Dataclass representing a security event.

**Attributes:**
- `event_type`: Type of event (EventType enum)
- `timestamp`: When the event occurred
- `security_level`: Associated security level
- `source`: Source component
- `message`: Event description
- `data`: Additional event data (dict)
- `event_id`: Unique identifier

**Methods:**
- `to_dict()`: Convert event to dictionary

### SecurityEventQueue

Thread-safe queue for managing security events.

**Methods:**
- `put(event)`: Add event to queue
- `get()`: Retrieve event from queue
- `register_handler(event_type, handler)`: Register event handler
- `unregister_handler(event_type, handler)`: Remove event handler
- `process_events()`: Async event processing (async)
- `get_history(event_type, security_level, limit)`: Get filtered event history
- `clear_history()`: Clear event history

### EncryptionManager

Manages encryption and decryption of sensitive data.

**Methods:**
- `__init__(key)`: Create with specific key
- `from_password(password, salt)`: Create from password (classmethod)
- `encrypt(data)`: Encrypt bytes
- `decrypt(encrypted_data)`: Decrypt bytes
- `encrypt_str(data)`: Encrypt string
- `decrypt_str(encrypted_data)`: Decrypt string
- `rotate_key(new_key)`: Rotate encryption key
- `re_encrypt(encrypted_data, new_key)`: Re-encrypt with new key

**Properties:**
- `key`: Current encryption key
- `salt`: Salt used for key derivation (if applicable)

## License

Apache License 2.0 - See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting pull requests.

## Security Considerations

- Always use strong passwords for password-based encryption
- Securely store encryption keys and salts
- Regularly rotate encryption keys for sensitive data
- Monitor security events and respond to critical alerts promptly
- Use appropriate security levels based on threat assessment

