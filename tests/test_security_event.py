"""Tests for SecurityEvent class."""
import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from security_modules import SecurityEvent


class TestSecurityEvent(unittest.TestCase):
    """Test cases for SecurityEvent."""
    
    def test_create_valid_event(self):
        """Test creating a valid security event."""
        event = SecurityEvent(
            event_type="test_event",
            severity="high",
            source="test_source",
            timestamp=datetime.now(),
            description="Test description"
        )
        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.severity, "high")
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.description, "Test description")
    
    def test_invalid_severity(self):
        """Test that invalid severity raises ValueError."""
        with self.assertRaises(ValueError):
            SecurityEvent(
                event_type="test_event",
                severity="invalid",
                source="test_source",
                timestamp=datetime.now(),
                description="Test description"
            )
    
    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        now = datetime.now()
        event = SecurityEvent(
            event_type="test_event",
            severity="critical",
            source="test_source",
            timestamp=now,
            description="Test description",
            metadata={"key": "value"}
        )
        event_dict = event.to_dict()
        self.assertEqual(event_dict["event_type"], "test_event")
        self.assertEqual(event_dict["severity"], "critical")
        self.assertEqual(event_dict["metadata"]["key"], "value")
    
    def test_all_severity_levels(self):
        """Test all valid severity levels."""
        severities = ["critical", "high", "medium", "low"]
        for severity in severities:
            event = SecurityEvent(
                event_type="test",
                severity=severity,
                source="test",
                timestamp=datetime.now(),
                description="test"
            )
            self.assertEqual(event.severity, severity)


if __name__ == '__main__':
    unittest.main()
