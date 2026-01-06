"""Event-driven architecture with queued security events."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from queue import Queue, Empty
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from .security_level import SecurityLevel

# Configure logger for this module
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of security events.
    
    Attributes:
        SECURITY_LEVEL_CHANGE: Security level changed
        CONNECTION_STATUS: Connection status changed
        INTRUSION_DETECTED: Potential intrusion detected
        AUTHENTICATION_FAILURE: Authentication failed
        ENCRYPTION_ERROR: Encryption operation failed
        SYSTEM_ALERT: General system alert
    """
    
    SECURITY_LEVEL_CHANGE = auto()
    CONNECTION_STATUS = auto()
    INTRUSION_DETECTED = auto()
    AUTHENTICATION_FAILURE = auto()
    ENCRYPTION_ERROR = auto()
    SYSTEM_ALERT = auto()


@dataclass
class SecurityEvent:
    """Represents a security event in the system.
    
    Attributes:
        event_type: Type of the security event
        timestamp: When the event occurred
        security_level: Security level associated with the event
        source: Source component that generated the event
        message: Human-readable description of the event
        data: Additional event data
        event_id: Unique identifier for the event
    """
    
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    security_level: SecurityLevel = SecurityLevel.NORMAL
    source: str = "system"
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    
    def __str__(self) -> str:
        """Return string representation of the event."""
        return (
            f"SecurityEvent({self.event_type.name}, "
            f"level={self.security_level.name}, "
            f"source={self.source}, "
            f"id={self.event_id[:8]})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation.
        
        Returns:
            Dictionary containing event data
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.name,
            "timestamp": self.timestamp.isoformat(),
            "security_level": self.security_level.name,
            "source": self.source,
            "message": self.message,
            "data": self.data,
        }


class SecurityEventQueue:
    """Event queue for managing security events.
    
    This class provides a thread-safe queue for security events with
    support for event handlers and filtering.
    """
    
    def __init__(self, maxsize: int = 0):
        """Initialize the security event queue.
        
        Args:
            maxsize: Maximum queue size (0 for unlimited)
        """
        self._queue: Queue[SecurityEvent] = Queue(maxsize=maxsize)
        self._handlers: Dict[EventType, List[Callable[[SecurityEvent], None]]] = {}
        self._running = False
        self._event_history: List[SecurityEvent] = []
        self._max_history = 1000
    
    def put(self, event: SecurityEvent, block: bool = True, timeout: Optional[float] = None) -> None:
        """Add an event to the queue.
        
        Args:
            event: Security event to add
            block: Whether to block if queue is full
            timeout: Maximum time to wait if blocking
            
        Raises:
            Full: If queue is full and blocking is disabled
        """
        self._queue.put(event, block=block, timeout=timeout)
        self._add_to_history(event)
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> SecurityEvent:
        """Get an event from the queue.
        
        Args:
            block: Whether to block if queue is empty
            timeout: Maximum time to wait if blocking
            
        Returns:
            Next security event from the queue
            
        Raises:
            Empty: If queue is empty and blocking is disabled
        """
        return self._queue.get(block=block, timeout=timeout)
    
    def get_nowait(self) -> SecurityEvent:
        """Get an event from the queue without blocking.
        
        Returns:
            Next security event from the queue
            
        Raises:
            Empty: If queue is empty
        """
        return self._queue.get_nowait()
    
    def size(self) -> int:
        """Get the current size of the queue.
        
        Returns:
            Number of events in the queue
        """
        return self._queue.qsize()
    
    def is_empty(self) -> bool:
        """Check if the queue is empty.
        
        Returns:
            True if queue is empty
        """
        return self._queue.empty()
    
    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[SecurityEvent], None]
    ) -> None:
        """Register a handler for a specific event type.
        
        Args:
            event_type: Type of events to handle
            handler: Callback function to handle events
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unregister_handler(
        self,
        event_type: EventType,
        handler: Callable[[SecurityEvent], None]
    ) -> None:
        """Unregister a handler for a specific event type.
        
        Args:
            event_type: Type of events
            handler: Handler to remove
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    async def process_events(self) -> None:
        """Process events from the queue asynchronously.
        
        This method runs continuously, processing events and
        calling registered handlers.
        """
        self._running = True
        while self._running:
            try:
                event = self.get(timeout=1.0)
                await self._handle_event(event)
            except Empty:
                # Allow other async tasks to run
                await asyncio.sleep(0.1)
    
    async def _handle_event(self, event: SecurityEvent) -> None:
        """Handle a security event by calling registered handlers.
        
        Args:
            event: Event to handle
        """
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                # Support both sync and async handlers
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                # Log error but continue processing
                logger.error(
                    "Error in event handler for %s: %s",
                    event.event_type.name,
                    str(e),
                    exc_info=True
                )
    
    def stop_processing(self) -> None:
        """Stop processing events."""
        self._running = False
    
    def _add_to_history(self, event: SecurityEvent) -> None:
        """Add event to history, maintaining maximum size.
        
        Args:
            event: Event to add to history
        """
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
    
    def get_history(
        self,
        event_type: Optional[EventType] = None,
        security_level: Optional[SecurityLevel] = None,
        limit: Optional[int] = None
    ) -> List[SecurityEvent]:
        """Get event history with optional filtering.
        
        Args:
            event_type: Filter by event type
            security_level: Filter by security level
            limit: Maximum number of events to return
            
        Returns:
            List of events matching the criteria
        """
        filtered = self._event_history
        
        if event_type is not None:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        if security_level is not None:
            filtered = [e for e in filtered if e.security_level == security_level]
        
        if limit is not None:
            filtered = filtered[-limit:]
        
        return filtered
    
    def clear_history(self) -> None:
        """Clear the event history."""
        self._event_history.clear()
