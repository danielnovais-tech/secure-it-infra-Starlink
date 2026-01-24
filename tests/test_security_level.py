"""Tests for security level module."""


from secure_it_infra.security_level import SecurityLevel


class TestSecurityLevel:
    """Test cases for SecurityLevel enum."""
    
    def test_security_levels_exist(self):
        """Test that all required security levels are defined."""
        assert SecurityLevel.NORMAL
        assert SecurityLevel.ELEVATED
        assert SecurityLevel.CRITICAL
        assert SecurityLevel.RECOVERY
    
    def test_security_level_str(self):
        """Test string representation of security levels."""
        assert str(SecurityLevel.NORMAL) == "NORMAL"
        assert str(SecurityLevel.ELEVATED) == "ELEVATED"
        assert str(SecurityLevel.CRITICAL) == "CRITICAL"
        assert str(SecurityLevel.RECOVERY) == "RECOVERY"
    
    def test_security_level_repr(self):
        """Test detailed representation of security levels."""
        assert repr(SecurityLevel.NORMAL) == "SecurityLevel.NORMAL"
        assert repr(SecurityLevel.ELEVATED) == "SecurityLevel.ELEVATED"
    
    def test_priority_ordering(self):
        """Test that security levels have correct priority ordering."""
        assert SecurityLevel.NORMAL.priority == 0
        assert SecurityLevel.ELEVATED.priority == 1
        assert SecurityLevel.CRITICAL.priority == 2
        assert SecurityLevel.RECOVERY.priority == 3
    
    def test_is_higher_than(self):
        """Test is_higher_than comparison method."""
        assert SecurityLevel.ELEVATED.is_higher_than(SecurityLevel.NORMAL)
        assert SecurityLevel.CRITICAL.is_higher_than(SecurityLevel.ELEVATED)
        assert SecurityLevel.RECOVERY.is_higher_than(SecurityLevel.CRITICAL)
        assert not SecurityLevel.NORMAL.is_higher_than(SecurityLevel.ELEVATED)
    
    def test_is_lower_than(self):
        """Test is_lower_than comparison method."""
        assert SecurityLevel.NORMAL.is_lower_than(SecurityLevel.ELEVATED)
        assert SecurityLevel.ELEVATED.is_lower_than(SecurityLevel.CRITICAL)
        assert SecurityLevel.CRITICAL.is_lower_than(SecurityLevel.RECOVERY)
        assert not SecurityLevel.ELEVATED.is_lower_than(SecurityLevel.NORMAL)
    
    def test_priority_comparison_reflexive(self):
        """Test that priority comparison is not reflexive."""
        assert not SecurityLevel.NORMAL.is_higher_than(SecurityLevel.NORMAL)
        assert not SecurityLevel.NORMAL.is_lower_than(SecurityLevel.NORMAL)
