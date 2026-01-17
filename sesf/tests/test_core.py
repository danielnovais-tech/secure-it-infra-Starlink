"""
Unit tests for SESF Framework Core
"""

import unittest
from sesf.core.framework import SESFFramework
from sesf.core.config import SESFConfig


class TestSESFFramework(unittest.TestCase):
    """Test cases for SESFFramework class."""
    
    def setUp(self):
        """Set up test framework instance."""
        self.framework = SESFFramework()
    
    def test_initialization(self):
        """Test framework initialization."""
        result = self.framework.initialize()
        self.assertTrue(result)
        self.assertTrue(self.framework.initialized)
    
    def test_module_loading(self):
        """Test that all modules are loaded."""
        self.framework.initialize()
        self.assertIn("authentication", self.framework.modules)
        self.assertIn("encryption", self.framework.modules)
        self.assertIn("network_security", self.framework.modules)
        self.assertIn("monitoring", self.framework.modules)
        self.assertIn("compliance", self.framework.modules)
    
    def test_get_status(self):
        """Test getting framework status."""
        self.framework.initialize()
        status = self.framework.get_status()
        self.assertIn("initialized", status)
        self.assertIn("modules", status)
        self.assertIn("version", status)
        self.assertEqual(status["version"], "1.0.0")
    
    def test_shutdown(self):
        """Test framework shutdown."""
        self.framework.initialize()
        self.framework.shutdown()
        self.assertFalse(self.framework.initialized)
        self.assertEqual(len(self.framework.modules), 0)


class TestSESFConfig(unittest.TestCase):
    """Test cases for SESFConfig class."""
    
    def setUp(self):
        """Set up test config instance."""
        self.config = SESFConfig()
    
    def test_default_config(self):
        """Test default configuration is loaded."""
        self.assertIsNotNone(self.config.config)
        self.assertIn("framework", self.config.config)
        self.assertIn("security", self.config.config)
    
    def test_get_config(self):
        """Test getting configuration values."""
        value = self.config.get("framework.name")
        self.assertEqual(value, "SESF")
        
        value = self.config.get("security.encryption_enabled")
        self.assertTrue(value)
    
    def test_set_config(self):
        """Test setting configuration values."""
        self.config.set("test.value", "test_data")
        self.assertEqual(self.config.get("test.value"), "test_data")
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config_dict = self.config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertIn("framework", config_dict)


if __name__ == "__main__":
    unittest.main()
