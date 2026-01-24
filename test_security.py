"""
Test suite for Starlink Security Infrastructure
"""

import asyncio
from starlink_security import (
    StarlinkSecurityFoundation,
    PolicyEnforcer,
    IncidentResponder,
    VPNManager,
    BackupManager,
    SecurityEvent
)
from datetime import datetime


async def test_policy_enforcer():
    """Test PolicyEnforcer functionality."""
    print("\n=== Testing PolicyEnforcer ===")
    foundation = StarlinkSecurityFoundation()
    policy_enforcer = PolicyEnforcer(foundation)
    
    assert policy_enforcer.initialize(), "PolicyEnforcer initialization failed"
    print("✓ PolicyEnforcer initialized successfully")
    
    # Test normal security level
    await policy_enforcer.enforce_security_level("normal")
    print("✓ Normal security level enforced")
    
    # Test critical security level
    await policy_enforcer.enforce_security_level("critical")
    print("✓ Critical security level enforced")
    
    # Verify policies
    assert 80 in policy_enforcer.active_policies["network_access"]["allowed_ports"]
    assert 443 in policy_enforcer.active_policies["network_access"]["allowed_ports"]
    assert policy_enforcer.active_policies["encryption"]["require_tls_1.3"] is True
    print("✓ Firewall and encryption policies verified")


async def test_incident_responder():
    """Test IncidentResponder functionality."""
    print("\n=== Testing IncidentResponder ===")
    foundation = StarlinkSecurityFoundation()
    incident_responder = IncidentResponder(foundation)
    
    assert incident_responder.initialize(), "IncidentResponder initialization failed"
    print("✓ IncidentResponder initialized successfully")
    
    # Test critical incident
    critical_event = SecurityEvent(
        event_type="malware_detected",
        severity="critical",
        source="test",
        message="Test malware event",
        timestamp=datetime.now(),
        metadata={}
    )
    await incident_responder.handle_incident(critical_event)
    assert len(incident_responder.incidents) == 1
    print("✓ Critical incident handled")
    
    # Test high severity incident
    high_event = SecurityEvent(
        event_type="breach_attempt",
        severity="high",
        source="test",
        message="Test breach event",
        timestamp=datetime.now(),
        metadata={}
    )
    await incident_responder.handle_incident(high_event)
    assert len(incident_responder.incidents) == 2
    print("✓ High severity incident handled")


async def test_vpn_manager():
    """Test VPNManager functionality."""
    print("\n=== Testing VPNManager ===")
    foundation = StarlinkSecurityFoundation()
    vpn_manager = VPNManager(foundation)
    
    assert vpn_manager.initialize(), "VPNManager initialization failed"
    print("✓ VPNManager initialized successfully")
    
    # Test status check
    await vpn_manager.check_vpn_status()
    print(f"✓ VPN status checked: {vpn_manager.vpn_status}")
    
    # Test connectivity check
    await vpn_manager.ensure_vpn_connectivity()
    print("✓ VPN connectivity checked")


async def test_backup_manager():
    """Test BackupManager functionality."""
    print("\n=== Testing BackupManager ===")
    foundation = StarlinkSecurityFoundation()
    backup_manager = BackupManager(foundation)
    
    assert backup_manager.initialize(), "BackupManager initialization failed"
    print("✓ BackupManager initialized successfully")
    
    # Verify backups were discovered
    assert len(backup_manager.backup_connections) == 2
    assert "cellular_backup" in backup_manager.backup_connections
    assert "satellite_backup" in backup_manager.backup_connections
    print(f"✓ Discovered {len(backup_manager.backup_connections)} backup connections")
    
    # Test availability check
    await backup_manager.check_backup_availability()
    print("✓ Backup availability checked")
    
    # Test failover evaluation
    await backup_manager.evaluate_failover_needs()
    print("✓ Failover evaluation completed")


async def test_integration():
    """Test integrated security infrastructure."""
    print("\n=== Testing Integrated Infrastructure ===")
    foundation = StarlinkSecurityFoundation()
    foundation.running = True
    
    # Create all components
    policy_enforcer = PolicyEnforcer(foundation)
    incident_responder = IncidentResponder(foundation)
    vpn_manager = VPNManager(foundation)
    backup_manager = BackupManager(foundation)
    
    # Initialize all
    policy_enforcer.initialize()
    incident_responder.initialize()
    vpn_manager.initialize()
    backup_manager.initialize()
    print("✓ All components initialized")
    
    # Register event handler
    foundation.register_event_handler(incident_responder.handle_incident)
    print("✓ Event handler registered")
    
    # Trigger test events
    await foundation.trigger_event(
        "test_event",
        "info",
        "test_suite",
        "Integration test event",
        {"test": True}
    )
    print("✓ Event triggered successfully")
    
    # Enforce security
    await policy_enforcer.enforce_security_level("critical")
    print("✓ Security policies enforced")
    
    foundation.running = False
    print("✓ Integration test completed")


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Starlink Security Infrastructure Test Suite")
    print("="*60)
    
    try:
        await test_policy_enforcer()
        await test_incident_responder()
        await test_vpn_manager()
        await test_backup_manager()
        await test_integration()
        
        print("\n" + "="*60)
        print("✅ All tests passed successfully!")
        print("="*60 + "\n")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
