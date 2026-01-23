"""
Connection Resilience Module

Provides failover mechanisms and resilience strategies for
intermittent Starlink connectivity typical in remote locations.
"""

import time
from typing import List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading


class ConnectionState(Enum):
    """Connection states"""
    CONNECTED = "connected"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"
    FAILOVER = "failover"
    RECOVERING = "recovering"


@dataclass
class BackupConnection:
    """Backup connection configuration"""
    name: str
    priority: int  # Lower is higher priority
    connection_type: str  # e.g., "cellular", "secondary_starlink", "radio"
    enabled: bool
    max_bandwidth_mbps: float
    latency_ms: float


@dataclass
class FailoverEvent:
    """Failover event record"""
    timestamp: float
    from_state: ConnectionState
    to_state: ConnectionState
    trigger: str
    backup_used: Optional[str]


class ConnectionResilience:
    """
    Manages connection resilience with automatic failover mechanisms
    designed for intermittent Starlink connectivity in remote locations.
    """
    
    def __init__(self, 
                 reconnect_attempts: int = 5,
                 reconnect_delay_seconds: int = 10,
                 failover_threshold_seconds: float = 30.0):
        """
        Initialize connection resilience manager
        
        Args:
            reconnect_attempts: Number of reconnection attempts before failover
            reconnect_delay_seconds: Delay between reconnection attempts
            failover_threshold_seconds: Time before triggering failover
        """
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay_seconds = reconnect_delay_seconds
        self.failover_threshold = failover_threshold_seconds
        
        self._state = ConnectionState.CONNECTED
        self._backup_connections: List[BackupConnection] = []
        self._active_backup: Optional[BackupConnection] = None
        self._failover_history: List[FailoverEvent] = []
        self._last_connected_time = time.time()
        self._reconnect_thread: Optional[threading.Thread] = None
        self._state_callbacks: List[Callable[[ConnectionState], None]] = []
    
    def register_state_callback(self, callback: Callable[[ConnectionState], None]) -> None:
        """Register a callback to be notified of state changes"""
        self._state_callbacks.append(callback)
    
    def add_backup_connection(self, backup: BackupConnection) -> None:
        """
        Add a backup connection option
        
        Args:
            backup: Backup connection configuration
        """
        self._backup_connections.append(backup)
        # Sort by priority (lower number = higher priority)
        self._backup_connections.sort(key=lambda x: x.priority)
    
    def get_backup_connections(self) -> List[BackupConnection]:
        """Get list of configured backup connections"""
        return self._backup_connections.copy()
    
    def _notify_state_change(self, new_state: ConnectionState) -> None:
        """Notify callbacks of state change"""
        old_state = self._state
        self._state = new_state
        
        for callback in self._state_callbacks:
            callback(new_state)
        
        # Record failover event
        if new_state == ConnectionState.FAILOVER:
            event = FailoverEvent(
                timestamp=time.time(),
                from_state=old_state,
                to_state=new_state,
                trigger="connection_lost",
                backup_used=self._active_backup.name if self._active_backup else None
            )
            self._failover_history.append(event)
    
    def handle_connection_loss(self) -> bool:
        """
        Handle connection loss with automatic recovery attempts
        
        Returns:
            True if connection recovered or failover successful
        """
        self._notify_state_change(ConnectionState.DISCONNECTED)
        
        # Attempt reconnection
        for attempt in range(self.reconnect_attempts):
            time.sleep(self.reconnect_delay_seconds)
            
            if self._attempt_reconnection():
                self._notify_state_change(ConnectionState.RECOVERING)
                self._last_connected_time = time.time()
                return True
        
        # If reconnection fails, attempt failover
        return self._initiate_failover()
    
    def _attempt_reconnection(self) -> bool:
        """
        Attempt to reconnect to primary connection
        
        Returns:
            True if reconnection successful
        """
        # Placeholder for actual reconnection logic
        # In production, this would attempt to re-establish Starlink connection
        return False
    
    def _initiate_failover(self) -> bool:
        """
        Initiate failover to backup connection
        
        Returns:
            True if failover successful
        """
        # Try each backup connection in priority order
        for backup in self._backup_connections:
            if not backup.enabled:
                continue
            
            if self._connect_to_backup(backup):
                self._active_backup = backup
                self._notify_state_change(ConnectionState.FAILOVER)
                return True
        
        return False
    
    def _connect_to_backup(self, backup: BackupConnection) -> bool:
        """
        Connect to a backup connection
        
        Args:
            backup: Backup connection to use
            
        Returns:
            True if connection successful
        """
        # Placeholder for actual backup connection logic
        # In production, this would establish connection via backup method
        return True
    
    def get_state(self) -> ConnectionState:
        """Get current connection state"""
        return self._state
    
    def is_using_backup(self) -> bool:
        """Check if currently using a backup connection"""
        return self._active_backup is not None
    
    def get_active_backup(self) -> Optional[BackupConnection]:
        """Get the currently active backup connection"""
        return self._active_backup
    
    def restore_primary_connection(self) -> bool:
        """
        Attempt to restore primary Starlink connection
        
        Returns:
            True if primary connection restored
        """
        if self._attempt_reconnection():
            self._active_backup = None
            self._notify_state_change(ConnectionState.CONNECTED)
            self._last_connected_time = time.time()
            return True
        return False
    
    def get_failover_history(self) -> List[FailoverEvent]:
        """Get history of failover events"""
        return self._failover_history.copy()
    
    def get_uptime_percentage(self, window_seconds: float = 3600) -> float:
        """
        Calculate connection uptime percentage
        
        Args:
            window_seconds: Time window to calculate over (default 1 hour)
            
        Returns:
            Uptime percentage (0-100)
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Calculate total downtime from failover events in window
        downtime = 0.0
        for i, event in enumerate(self._failover_history):
            if event.timestamp < window_start:
                continue
            
            # Find when connection was restored
            restore_time = now
            for future_event in self._failover_history[i+1:]:
                if future_event.to_state in [ConnectionState.CONNECTED, ConnectionState.RECOVERING]:
                    restore_time = future_event.timestamp
                    break
            
            downtime += min(restore_time, now) - max(event.timestamp, window_start)
        
        uptime_percentage = ((window_seconds - downtime) / window_seconds) * 100
        return max(0, min(100, uptime_percentage))
    
    def enable_queue_mode(self) -> None:
        """
        Enable queue mode for operations during disconnection.
        Operations are queued and executed when connection is restored.
        """
        # Placeholder for queue mode implementation
        pass
    
    def get_queued_operations_count(self) -> int:
        """Get count of queued operations waiting for connection"""
        # Placeholder - would return actual queue size
        return 0
