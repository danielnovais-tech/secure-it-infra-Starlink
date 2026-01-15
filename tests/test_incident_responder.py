"""Tests for IncidentResponder class."""
import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from security_modules import IncidentResponder, SecurityEvent


class TestIncidentResponder(unittest.IsolatedAsyncioTestCase):
    """Test cases for IncidentResponder."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        self.responder = IncidentResponder()
    
    def test_initialization(self):
        """Test responder initialization."""
        self.assertEqual(len(self.responder.incidents), 0)
        self.assertIn("critical", self.responder.response_actions)
        self.assertIn("high", self.responder.response_actions)
    
    async def test_handle_critical_incident(self):
        """Test handling a critical incident."""
        event = SecurityEvent(
            event_type="critical_test",
            severity="critical",
            source="test",
            timestamp=datetime.now(),
            description="Critical test event"
        )
        await self.responder.handle_incident(event)
        self.assertEqual(len(self.responder.incidents), 1)
        self.assertEqual(self.responder.incidents[0], event)
    
    async def test_handle_high_incident(self):
        """Test handling a high severity incident."""
        event = SecurityEvent(
            event_type="high_test",
            severity="high",
            source="test",
            timestamp=datetime.now(),
            description="High test event"
        )
        await self.responder.handle_incident(event)
        self.assertEqual(len(self.responder.incidents), 1)
    
    async def test_handle_multiple_incidents(self):
        """Test handling multiple incidents."""
        events = [
            SecurityEvent(
                event_type=f"test_{i}",
                severity="critical",
                source="test",
                timestamp=datetime.now(),
                description=f"Test event {i}"
            )
            for i in range(3)
        ]
        
        for event in events:
            await self.responder.handle_incident(event)
        
        self.assertEqual(len(self.responder.incidents), 3)


if __name__ == '__main__':
    unittest.main()
