"""Tests for package initialization."""

import secure_it_infra


class TestPackageInit:
    """Test cases for package initialization."""
    
    def test_version(self):
        """Test that package has version."""
        assert hasattr(secure_it_infra, '__version__')
        assert secure_it_infra.__version__ == "0.1.0"
    
    def test_exports_security_level(self):
        """Test that SecurityLevel is exported."""
        assert hasattr(secure_it_infra, 'SecurityLevel')
    
    def test_exports_connection_type(self):
        """Test that ConnectionType is exported."""
        assert hasattr(secure_it_infra, 'ConnectionType')
    
    def test_exports_security_event(self):
        """Test that SecurityEvent is exported."""
        assert hasattr(secure_it_infra, 'SecurityEvent')
    
    def test_exports_security_event_queue(self):
        """Test that SecurityEventQueue is exported."""
        assert hasattr(secure_it_infra, 'SecurityEventQueue')
    
    def test_exports_event_type(self):
        """Test that EventType is exported."""
        assert hasattr(secure_it_infra, 'EventType')
    
    def test_exports_encryption_manager(self):
        """Test that EncryptionManager is exported."""
        assert hasattr(secure_it_infra, 'EncryptionManager')
    
    def test_exports_encryption_error(self):
        """Test that EncryptionError is exported."""
        assert hasattr(secure_it_infra, 'EncryptionError')
    
    def test_all_contains_expected_items(self):
        """Test that __all__ contains expected exports."""
        expected = [
            "SecurityLevel",
            "ConnectionType",
            "SecurityEvent",
            "SecurityEventQueue",
            "EventType",
            "EncryptionManager",
            "EncryptionError",
        ]
        assert all(item in secure_it_infra.__all__ for item in expected)
