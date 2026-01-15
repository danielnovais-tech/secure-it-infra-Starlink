"""Tests for connection type module."""

import pytest

from secure_it_infra.connection_type import ConnectionType


class TestConnectionType:
    """Test cases for ConnectionType enum."""
    
    def test_connection_types_exist(self):
        """Test that all required connection types are defined."""
        assert ConnectionType.STARLINK_ONLY
        assert ConnectionType.HYBRID
        assert ConnectionType.FAILOVER
    
    def test_connection_type_str(self):
        """Test string representation of connection types."""
        assert str(ConnectionType.STARLINK_ONLY) == "STARLINK-ONLY"
        assert str(ConnectionType.HYBRID) == "HYBRID"
        assert str(ConnectionType.FAILOVER) == "FAILOVER"
    
    def test_connection_type_repr(self):
        """Test detailed representation of connection types."""
        assert repr(ConnectionType.STARLINK_ONLY) == "ConnectionType.STARLINK_ONLY"
        assert repr(ConnectionType.HYBRID) == "ConnectionType.HYBRID"
    
    def test_supports_redundancy(self):
        """Test redundancy support property."""
        assert not ConnectionType.STARLINK_ONLY.supports_redundancy
        assert ConnectionType.HYBRID.supports_redundancy
        assert ConnectionType.FAILOVER.supports_redundancy
    
    def test_is_satellite_only(self):
        """Test satellite-only property."""
        assert ConnectionType.STARLINK_ONLY.is_satellite_only
        assert not ConnectionType.HYBRID.is_satellite_only
        assert not ConnectionType.FAILOVER.is_satellite_only
