"""Example usage of the Security Monitoring System."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from security_manager import SecurityManager


async def main():
    """Demonstrate the security monitoring system."""
    print("=" * 60)
    print("Security IT Infrastructure - Security Monitoring System")
    print("=" * 60)
    print()
    
    # Initialize the security manager
    manager = SecurityManager()
    await manager.start()
    
    print("1. Creating security events...")
    print("-" * 60)
    
    # Create some security events
    manager.create_and_queue_event(
        event_type="unauthorized_access_attempt",
        severity="critical",
        source="firewall",
        description="Multiple failed login attempts from suspicious IP",
        metadata={"ip": "192.168.1.100", "attempts": 5}
    )
    
    manager.create_and_queue_event(
        event_type="suspicious_network_activity",
        severity="high",
        source="network_monitor",
        description="Unusual outbound traffic detected",
        metadata={"bytes": 1000000, "destination": "unknown"}
    )
    
    manager.create_and_queue_event(
        event_type="file_integrity_check",
        severity="medium",
        source="file_monitor",
        description="System file modified",
        metadata={"file": "/etc/passwd"}
    )
    
    manager.create_and_queue_event(
        event_type="routine_scan",
        severity="low",
        source="scanner",
        description="Scheduled security scan completed",
        metadata={"vulnerabilities_found": 0}
    )
    
    # Wait for events to be processed
    await asyncio.sleep(0.5)
    
    print("\n2. Adjusting security level to 'high'...")
    print("-" * 60)
    await manager.adjust_security_level("high")
    
    print("\n3. Adjusting security level to 'critical'...")
    print("-" * 60)
    await manager.adjust_security_level("critical")
    
    # Wait a bit more
    await asyncio.sleep(0.5)
    
    print("\n4. Summary")
    print("-" * 60)
    print(f"Total events logged: {len(manager.get_event_log())}")
    print(f"Total incidents handled: {len(manager.get_incidents())}")
    
    print("\nEvent Log:")
    for event in manager.get_event_log():
        print(f"  - [{event.severity.upper()}] {event.event_type}: {event.description}")
    
    print("\nIncidents Handled:")
    for incident in manager.get_incidents():
        print(f"  - [{incident.severity.upper()}] {incident.event_type}: {incident.description}")
    
    # Stop the manager
    await manager.stop()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
