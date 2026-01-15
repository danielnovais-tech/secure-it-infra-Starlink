"""Tests for PolicyEnforcer class."""
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from security_modules import PolicyEnforcer


class TestPolicyEnforcer(unittest.IsolatedAsyncioTestCase):
    """Test cases for PolicyEnforcer."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        self.enforcer = PolicyEnforcer()
    
    def test_initialization(self):
        """Test enforcer initialization."""
        self.assertEqual(self.enforcer.current_level, "medium")
        self.assertIn("low", self.enforcer.policies)
        self.assertIn("medium", self.enforcer.policies)
        self.assertIn("high", self.enforcer.policies)
        self.assertIn("critical", self.enforcer.policies)
    
    async def test_apply_valid_level(self):
        """Test applying a valid security level."""
        await self.enforcer.apply_security_level("high")
        self.assertEqual(self.enforcer.current_level, "high")
    
    async def test_apply_invalid_level(self):
        """Test applying an invalid security level."""
        with self.assertRaises(ValueError):
            await self.enforcer.apply_security_level("invalid")
    
    async def test_apply_all_levels(self):
        """Test applying all valid security levels."""
        levels = ["low", "medium", "high", "critical"]
        for level in levels:
            await self.enforcer.apply_security_level(level)
            self.assertEqual(self.enforcer.current_level, level)


if __name__ == '__main__':
    unittest.main()
