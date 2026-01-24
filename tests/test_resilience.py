"""
Tests for Connection Resilience Module
"""

from starlink_security.resilience import (
    ConnectionResilience,
    ConnectionState,
    BackupConnection
)


def test_resilience_initialization():
    """Test resilience manager initialization"""
    resilience = ConnectionResilience(
        reconnect_attempts=5,
        reconnect_delay_seconds=10,
        failover_threshold_seconds=30.0
    )
    
    assert resilience.reconnect_attempts == 5
    assert resilience.reconnect_delay_seconds == 10
    assert resilience._state == ConnectionState.CONNECTED


def test_add_backup_connection():
    """Test adding backup connections"""
    resilience = ConnectionResilience()
    
    backup1 = BackupConnection(
        name="cellular",
        priority=1,
        connection_type="cellular",
        enabled=True,
        max_bandwidth_mbps=25.0,
        latency_ms=80.0
    )
    
    backup2 = BackupConnection(
        name="satellite",
        priority=2,
        connection_type="satellite",
        enabled=True,
        max_bandwidth_mbps=50.0,
        latency_ms=600.0
    )
    
    resilience.add_backup_connection(backup1)
    resilience.add_backup_connection(backup2)
    
    backups = resilience.get_backup_connections()
    assert len(backups) == 2
    # Should be sorted by priority
    assert backups[0].priority == 1


def test_state_callback():
    """Test state change callbacks"""
    resilience = ConnectionResilience()
    callback_called = [False]
    new_state_received = [None]
    
    def test_callback(state):
        callback_called[0] = True
        new_state_received[0] = state
    
    resilience.register_state_callback(test_callback)
    resilience._notify_state_change(ConnectionState.DEGRADED)
    
    assert callback_called[0] is True
    assert new_state_received[0] == ConnectionState.DEGRADED


def test_get_state():
    """Test getting current state"""
    resilience = ConnectionResilience()
    assert resilience.get_state() == ConnectionState.CONNECTED


def test_backup_usage():
    """Test backup connection usage tracking"""
    resilience = ConnectionResilience()
    
    assert resilience.is_using_backup() is False
    assert resilience.get_active_backup() is None


def test_uptime_calculation():
    """Test uptime percentage calculation"""
    resilience = ConnectionResilience()
    
    # With no failover events, should be 100%
    uptime = resilience.get_uptime_percentage()
    assert uptime == 100.0


def test_failover_history():
    """Test failover event history"""
    resilience = ConnectionResilience()
    
    # Initially empty
    history = resilience.get_failover_history()
    assert len(history) == 0
