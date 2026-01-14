"""Tests for event queue module."""

import asyncio
from datetime import datetime
from queue import Empty

import pytest

from secure_it_infra.event_queue import (
    EventType,
    SecurityEvent,
    SecurityEventQueue,
)
from secure_it_infra.security_level import SecurityLevel


class TestEventType:
    """Test cases for EventType enum."""
    
    def test_event_types_exist(self):
        """Test that all required event types are defined."""
        assert EventType.SECURITY_LEVEL_CHANGE
        assert EventType.CONNECTION_STATUS
        assert EventType.INTRUSION_DETECTED
        assert EventType.AUTHENTICATION_FAILURE
        assert EventType.ENCRYPTION_ERROR
        assert EventType.SYSTEM_ALERT


class TestSecurityEvent:
    """Test cases for SecurityEvent class."""
    
    def test_create_event(self):
        """Test creating a security event."""
        event = SecurityEvent(
            event_type=EventType.SYSTEM_ALERT,
            message="Test event",
        )
        assert event.event_type == EventType.SYSTEM_ALERT
        assert event.message == "Test event"
        assert event.security_level == SecurityLevel.NORMAL
        assert event.source == "system"
        assert event.event_id is not None
    
    def test_event_with_custom_values(self):
        """Test creating an event with custom values."""
        event = SecurityEvent(
            event_type=EventType.INTRUSION_DETECTED,
            security_level=SecurityLevel.CRITICAL,
            source="firewall",
            message="Intrusion detected",
            data={"ip": "192.168.1.100"},
        )
        assert event.security_level == SecurityLevel.CRITICAL
        assert event.source == "firewall"
        assert event.data["ip"] == "192.168.1.100"
    
    def test_event_timestamp(self):
        """Test that event has timestamp."""
        event = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        assert isinstance(event.timestamp, datetime)
    
    def test_event_str(self):
        """Test string representation of event."""
        event = SecurityEvent(
            event_type=EventType.SYSTEM_ALERT,
            security_level=SecurityLevel.ELEVATED,
            source="test",
        )
        event_str = str(event)
        assert "SYSTEM_ALERT" in event_str
        assert "ELEVATED" in event_str
        assert "test" in event_str
    
    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = SecurityEvent(
            event_type=EventType.CONNECTION_STATUS,
            security_level=SecurityLevel.NORMAL,
            source="network",
            message="Connection established",
            data={"status": "connected"},
        )
        event_dict = event.to_dict()
        
        assert event_dict["event_type"] == "CONNECTION_STATUS"
        assert event_dict["security_level"] == "NORMAL"
        assert event_dict["source"] == "network"
        assert event_dict["message"] == "Connection established"
        assert event_dict["data"]["status"] == "connected"
        assert "event_id" in event_dict
        assert "timestamp" in event_dict


class TestSecurityEventQueue:
    """Test cases for SecurityEventQueue class."""
    
    def test_create_queue(self):
        """Test creating an event queue."""
        queue = SecurityEventQueue()
        assert queue.is_empty()
        assert queue.size() == 0
    
    def test_put_and_get_event(self):
        """Test adding and retrieving events."""
        queue = SecurityEventQueue()
        event = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        
        queue.put(event)
        assert not queue.is_empty()
        assert queue.size() == 1
        
        retrieved = queue.get()
        assert retrieved.event_id == event.event_id
        assert queue.is_empty()
    
    def test_get_nowait_on_empty_queue(self):
        """Test get_nowait raises Empty on empty queue."""
        queue = SecurityEventQueue()
        with pytest.raises(Empty):
            queue.get_nowait()
    
    def test_queue_with_maxsize(self):
        """Test queue with maximum size."""
        from queue import Full
        
        queue = SecurityEventQueue(maxsize=2)
        
        event1 = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        event2 = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        
        queue.put(event1)
        queue.put(event2)
        
        # Third event should not block if we use timeout
        event3 = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        with pytest.raises(Full):
            queue.put(event3, block=False)
    
    def test_event_history(self):
        """Test event history tracking."""
        queue = SecurityEventQueue()
        
        event1 = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        event2 = SecurityEvent(event_type=EventType.CONNECTION_STATUS)
        
        queue.put(event1)
        queue.put(event2)
        
        history = queue.get_history()
        assert len(history) == 2
        assert history[0].event_id == event1.event_id
        assert history[1].event_id == event2.event_id
    
    def test_filter_history_by_event_type(self):
        """Test filtering history by event type."""
        queue = SecurityEventQueue()
        
        event1 = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        event2 = SecurityEvent(event_type=EventType.CONNECTION_STATUS)
        event3 = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        
        queue.put(event1)
        queue.put(event2)
        queue.put(event3)
        
        history = queue.get_history(event_type=EventType.SYSTEM_ALERT)
        assert len(history) == 2
    
    def test_filter_history_by_security_level(self):
        """Test filtering history by security level."""
        queue = SecurityEventQueue()
        
        event1 = SecurityEvent(
            event_type=EventType.SYSTEM_ALERT,
            security_level=SecurityLevel.NORMAL
        )
        event2 = SecurityEvent(
            event_type=EventType.INTRUSION_DETECTED,
            security_level=SecurityLevel.CRITICAL
        )
        
        queue.put(event1)
        queue.put(event2)
        
        history = queue.get_history(security_level=SecurityLevel.CRITICAL)
        assert len(history) == 1
        assert history[0].event_id == event2.event_id
    
    def test_limit_history(self):
        """Test limiting history results."""
        queue = SecurityEventQueue()
        
        for i in range(10):
            event = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
            queue.put(event)
        
        history = queue.get_history(limit=5)
        assert len(history) == 5
    
    def test_clear_history(self):
        """Test clearing event history."""
        queue = SecurityEventQueue()
        
        event = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        queue.put(event)
        
        assert len(queue.get_history()) == 1
        
        queue.clear_history()
        assert len(queue.get_history()) == 0
    
    def test_register_handler(self):
        """Test registering an event handler."""
        queue = SecurityEventQueue()
        handled_events = []
        
        def handler(event: SecurityEvent):
            handled_events.append(event)
        
        queue.register_handler(EventType.SYSTEM_ALERT, handler)
        
        # Verify handler was registered (internal check)
        assert EventType.SYSTEM_ALERT in queue._handlers
        assert handler in queue._handlers[EventType.SYSTEM_ALERT]
    
    def test_unregister_handler(self):
        """Test unregistering an event handler."""
        queue = SecurityEventQueue()
        
        def handler(event: SecurityEvent):
            pass
        
        queue.register_handler(EventType.SYSTEM_ALERT, handler)
        queue.unregister_handler(EventType.SYSTEM_ALERT, handler)
        
        assert handler not in queue._handlers.get(EventType.SYSTEM_ALERT, [])
    
    @pytest.mark.asyncio
    async def test_async_event_processing(self):
        """Test asynchronous event processing."""
        queue = SecurityEventQueue()
        handled_events = []
        
        def handler(event: SecurityEvent):
            handled_events.append(event)
        
        queue.register_handler(EventType.SYSTEM_ALERT, handler)
        
        # Start processing in background
        process_task = asyncio.create_task(queue.process_events())
        
        # Add event
        event = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        queue.put(event)
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Stop processing
        queue.stop_processing()
        await asyncio.sleep(0.2)
        
        # Cancel the task
        process_task.cancel()
        try:
            await process_task
        except asyncio.CancelledError:
            pass
        
        # Verify handler was called
        assert len(handled_events) == 1
        assert handled_events[0].event_id == event.event_id
    
    @pytest.mark.asyncio
    async def test_async_handler(self):
        """Test async event handler."""
        queue = SecurityEventQueue()
        handled_events = []
        
        async def async_handler(event: SecurityEvent):
            await asyncio.sleep(0.01)
            handled_events.append(event)
        
        queue.register_handler(EventType.SYSTEM_ALERT, async_handler)
        
        # Start processing
        process_task = asyncio.create_task(queue.process_events())
        
        # Add event
        event = SecurityEvent(event_type=EventType.SYSTEM_ALERT)
        queue.put(event)
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Stop processing
        queue.stop_processing()
        await asyncio.sleep(0.2)
        
        # Cancel the task
        process_task.cancel()
        try:
            await process_task
        except asyncio.CancelledError:
            pass
        
        # Verify async handler was called
        assert len(handled_events) == 1
