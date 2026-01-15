"""Example usage of the Secure IT Infrastructure for Starlink."""

import asyncio
from datetime import datetime

from secure_it_infra import (
    SecurityLevel,
    ConnectionType,
    SecurityEvent,
    SecurityEventQueue,
    EventType,
    EncryptionManager,
)


def example_security_levels():
    """Demonstrate security level usage."""
    print("=== Security Levels Example ===\n")
    
    # Create security levels
    normal = SecurityLevel.NORMAL
    elevated = SecurityLevel.ELEVATED
    critical = SecurityLevel.CRITICAL
    recovery = SecurityLevel.RECOVERY
    
    print(f"Security Levels: {normal}, {elevated}, {critical}, {recovery}")
    print(f"Critical Priority: {critical.priority}")
    print(f"Is Critical higher than Elevated? {critical.is_higher_than(elevated)}")
    print(f"Is Normal lower than Recovery? {normal.is_lower_than(recovery)}")
    print()


def example_connection_types():
    """Demonstrate connection type usage."""
    print("=== Connection Types Example ===\n")
    
    # Create connection types
    starlink = ConnectionType.STARLINK_ONLY
    hybrid = ConnectionType.HYBRID
    failover = ConnectionType.FAILOVER
    
    print(f"Connection Types: {starlink}, {hybrid}, {failover}")
    print(f"Starlink-only satellite? {starlink.is_satellite_only}")
    print(f"Hybrid supports redundancy? {hybrid.supports_redundancy}")
    print(f"Failover supports redundancy? {failover.supports_redundancy}")
    print()


def example_event_queue():
    """Demonstrate event queue usage."""
    print("=== Event Queue Example ===\n")
    
    # Create event queue
    queue = SecurityEventQueue()
    
    # Create and add events
    event1 = SecurityEvent(
        event_type=EventType.SECURITY_LEVEL_CHANGE,
        security_level=SecurityLevel.ELEVATED,
        source="security_monitor",
        message="Security level elevated due to unusual activity",
        data={"previous_level": "NORMAL", "reason": "multiple_failed_logins"},
    )
    
    event2 = SecurityEvent(
        event_type=EventType.CONNECTION_STATUS,
        security_level=SecurityLevel.NORMAL,
        source="network_manager",
        message="Starlink connection established",
        data={"connection_type": "STARLINK_ONLY", "latency_ms": 45},
    )
    
    event3 = SecurityEvent(
        event_type=EventType.INTRUSION_DETECTED,
        security_level=SecurityLevel.CRITICAL,
        source="ids",
        message="Potential intrusion detected",
        data={"source_ip": "192.168.1.100", "attack_type": "port_scan"},
    )
    
    # Add events to queue
    queue.put(event1)
    queue.put(event2)
    queue.put(event3)
    
    print(f"Queue size: {queue.size()}")
    print(f"Queue empty? {queue.is_empty()}\n")
    
    # Process events
    print("Processing events:")
    while not queue.is_empty():
        event = queue.get()
        print(f"  - {event}")
        print(f"    Message: {event.message}")
        print(f"    Data: {event.data}")
    
    print(f"\nQueue size after processing: {queue.size()}")
    
    # Check event history
    print(f"\nEvent history count: {len(queue.get_history())}")
    critical_events = queue.get_history(security_level=SecurityLevel.CRITICAL)
    print(f"Critical events in history: {len(critical_events)}")
    print()


async def example_async_event_processing():
    """Demonstrate async event processing with handlers."""
    print("=== Async Event Processing Example ===\n")
    
    queue = SecurityEventQueue()
    
    # Track handled events
    handled_events = []
    
    # Register event handlers
    def handle_security_change(event: SecurityEvent):
        handled_events.append(event)
        print(f"  Security level changed: {event.message}")
    
    def handle_intrusion(event: SecurityEvent):
        handled_events.append(event)
        print(f"  ⚠️  INTRUSION DETECTED: {event.message}")
        print(f"     Data: {event.data}")
    
    queue.register_handler(EventType.SECURITY_LEVEL_CHANGE, handle_security_change)
    queue.register_handler(EventType.INTRUSION_DETECTED, handle_intrusion)
    
    # Start async processing
    process_task = asyncio.create_task(queue.process_events())
    
    # Add events
    print("Adding events to queue...")
    queue.put(SecurityEvent(
        event_type=EventType.SECURITY_LEVEL_CHANGE,
        security_level=SecurityLevel.ELEVATED,
        message="Elevated security due to network anomaly",
    ))
    
    await asyncio.sleep(0.1)
    
    queue.put(SecurityEvent(
        event_type=EventType.INTRUSION_DETECTED,
        security_level=SecurityLevel.CRITICAL,
        message="Unauthorized access attempt",
        data={"source": "external", "blocked": True},
    ))
    
    # Wait for processing
    await asyncio.sleep(0.2)
    
    # Stop processing
    queue.stop_processing()
    await asyncio.sleep(0.1)
    process_task.cancel()
    
    try:
        await process_task
    except asyncio.CancelledError:
        pass
    
    print(f"\nTotal events handled: {len(handled_events)}")
    print()


def example_encryption():
    """Demonstrate encryption management."""
    print("=== Encryption Management Example ===\n")
    
    # Create encryption manager with auto-generated key
    manager = EncryptionManager()
    
    # Encrypt sensitive data
    sensitive_data = "Starlink API Key: sk_live_abc123xyz789"
    encrypted = manager.encrypt_str(sensitive_data)
    
    print(f"Original: {sensitive_data}")
    print(f"Encrypted: {encrypted[:50]}...")
    
    # Decrypt data
    decrypted = manager.decrypt_str(encrypted)
    print(f"Decrypted: {decrypted}")
    print(f"Match: {decrypted == sensitive_data}\n")
    
    # Create manager from password
    print("Creating manager from password...")
    password_manager = EncryptionManager.from_password("my_secure_password_123")
    
    # Encrypt configuration data
    config_data = '{"endpoint": "starlink.api.com", "timeout": 30}'
    encrypted_config = password_manager.encrypt_str(config_data)
    print(f"Encrypted config: {encrypted_config[:50]}...")
    
    # Recreate manager with same password and salt
    restored_manager = EncryptionManager.from_password(
        "my_secure_password_123",
        salt=password_manager.salt
    )
    
    decrypted_config = restored_manager.decrypt_str(encrypted_config)
    print(f"Decrypted config: {decrypted_config}")
    print(f"Match: {decrypted_config == config_data}\n")
    
    # Key rotation
    print("Demonstrating key rotation...")
    original_key = manager.key
    manager.rotate_key()
    print(f"Key rotated: {original_key != manager.key}")
    print()


def example_integrated_scenario():
    """Demonstrate an integrated security scenario."""
    print("=== Integrated Security Scenario ===\n")
    
    # Initialize components
    queue = SecurityEventQueue()
    encryption_manager = EncryptionManager.from_password("starlink_secure_2024")
    
    # Simulate security monitoring
    print("1. System starts in NORMAL security level")
    current_level = SecurityLevel.NORMAL
    
    # Detect suspicious activity
    print("\n2. Suspicious activity detected, elevating security...")
    current_level = SecurityLevel.ELEVATED
    
    queue.put(SecurityEvent(
        event_type=EventType.SECURITY_LEVEL_CHANGE,
        security_level=current_level,
        source="security_monitor",
        message="Security elevated: Multiple failed authentication attempts",
        data={"failed_attempts": 5, "source_ip": "10.0.0.50"},
    ))
    
    # Switch to failover connection
    print("3. Switching to failover connection mode...")
    connection = ConnectionType.FAILOVER
    
    queue.put(SecurityEvent(
        event_type=EventType.CONNECTION_STATUS,
        security_level=SecurityLevel.NORMAL,
        source="network_manager",
        message=f"Connection switched to {connection}",
        data={"previous": "STARLINK_ONLY", "current": str(connection)},
    ))
    
    # Encrypt sensitive credentials
    print("4. Encrypting sensitive credentials...")
    credentials = {
        "api_key": "sk_live_abc123",
        "token": "bearer_xyz789",
    }
    encrypted_creds = encryption_manager.encrypt_str(str(credentials))
    print(f"   Credentials encrypted: {encrypted_creds[:40]}...")
    
    # Critical security event
    print("\n5. CRITICAL: Intrusion detected!")
    current_level = SecurityLevel.CRITICAL
    
    queue.put(SecurityEvent(
        event_type=EventType.INTRUSION_DETECTED,
        security_level=current_level,
        source="intrusion_detection",
        message="Unauthorized access attempt detected",
        data={
            "source_ip": "203.0.113.45",
            "target_service": "admin_panel",
            "blocked": True,
        },
    ))
    
    # Process events
    print("\n6. Processing security events...")
    event_count = 0
    while not queue.is_empty():
        event = queue.get()
        event_count += 1
        print(f"   Event {event_count}: [{event.security_level.name}] {event.message}")
    
    # Summary
    print(f"\n7. Summary:")
    print(f"   - Current Security Level: {current_level.name}")
    print(f"   - Connection Type: {connection}")
    print(f"   - Events Processed: {event_count}")
    print(f"   - Critical Events: {len(queue.get_history(security_level=SecurityLevel.CRITICAL))}")
    print(f"   - Credentials Encrypted: Yes")
    print()


def main():
    """Run all examples."""
    print("=" * 60)
    print("Secure IT Infrastructure for Starlink - Examples")
    print("=" * 60)
    print()
    
    example_security_levels()
    example_connection_types()
    example_event_queue()
    
    # Run async example
    asyncio.run(example_async_event_processing())
    
    example_encryption()
    example_integrated_scenario()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
