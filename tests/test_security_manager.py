"""Tests for SecurityManager class."""
import unittest
import asyncio
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from security_manager import SecurityManager
from security_modules import SecurityEvent


class TestSecurityManager(unittest.TestCase):
    """Test cases for SecurityManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = SecurityManager()
    
    def test_initialization(self):
        """Test manager initialization."""
        self.assertIn('policy_enforcer', self.manager.security_modules)
        self.assertIn('incident_responder', self.manager.security_modules)
        self.assertIsNotNone(self.manager.events_queue)
        self.assertEqual(len(self.manager.event_log), 0)
    
    def test_add_event(self):
        """Test adding an event to the queue."""
        event = SecurityEvent(
            event_type="test_event",
            severity="high",
            source="test",
            timestamp=datetime.now(),
            description="Test event"
        )
        self.manager.add_event(event)
        self.assertFalse(self.manager.events_queue.empty())
    
    def test_create_and_queue_event(self):
        """Test creating and queuing an event."""
        self.manager.create_and_queue_event(
            event_type="test",
            severity="critical",
            source="test",
            description="Test event"
        )
        self.assertFalse(self.manager.events_queue.empty())
    
    def test_log_event(self):
        """Test logging an event."""
        event = SecurityEvent(
            event_type="test_event",
            severity="medium",
            source="test",
            timestamp=datetime.now(),
            description="Test event"
        )
        self.manager._log_event(event)
        self.assertEqual(len(self.manager.event_log), 1)
        self.assertEqual(self.manager.event_log[0], event)
    
    def test_get_event_log(self):
        """Test getting event log."""
        event = SecurityEvent(
            event_type="test",
            severity="low",
            source="test",
            timestamp=datetime.now(),
            description="Test"
        )
        self.manager._log_event(event)
        log = self.manager.get_event_log()
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0], event)


class TestSecurityManagerAsync(unittest.IsolatedAsyncioTestCase):
    """Async test cases for SecurityManager."""
    
    async def asyncSetUp(self):
        """Set up async test fixtures."""
        self.manager = SecurityManager()
    
    async def test_adjust_security_level(self):
        """Test adjusting security level."""
        await self.manager.adjust_security_level("high")
        self.assertEqual(
            self.manager.security_modules['policy_enforcer'].current_level,
            "high"
        )
    
    async def test_process_events(self):
        """Test processing events."""
        event = SecurityEvent(
            event_type="test_event",
            severity="critical",
            source="test",
            timestamp=datetime.now(),
            description="Test critical event"
        )
        self.manager.add_event(event)
        await self.manager._process_events()
        
        # Event should be logged
        self.assertEqual(len(self.manager.event_log), 1)
        # Critical event should create an incident
        self.assertEqual(len(self.manager.get_incidents()), 1)
    
    async def test_handle_high_severity_event(self):
        """Test handling high severity event."""
        event = SecurityEvent(
            event_type="test_high",
            severity="high",
            source="test",
            timestamp=datetime.now(),
            description="Test high severity"
        )
        await self.manager._handle_event(event)
        
        # Should be logged
        self.assertEqual(len(self.manager.event_log), 1)
        # Should create incident
        self.assertEqual(len(self.manager.get_incidents()), 1)
    
    async def test_handle_low_severity_event(self):
        """Test handling low severity event."""
        event = SecurityEvent(
            event_type="test_low",
            severity="low",
            source="test",
            timestamp=datetime.now(),
            description="Test low severity"
        )
        await self.manager._handle_event(event)
        
        # Should be logged
        self.assertEqual(len(self.manager.event_log), 1)
        # Should NOT create incident (only critical and high do)
        self.assertEqual(len(self.manager.get_incidents()), 0)


if __name__ == '__main__':
    unittest.main()
