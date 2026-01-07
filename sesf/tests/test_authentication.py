"""
Unit tests for SESF Authentication Module
"""

import unittest
from sesf.modules.authentication import AuthenticationModule


class TestAuthenticationModule(unittest.TestCase):
    """Test cases for AuthenticationModule."""
    
    def setUp(self):
        """Set up test authentication module."""
        self.auth = AuthenticationModule({
            "method": "multi-factor",
            "session_timeout": 3600,
            "max_login_attempts": 3
        })
    
    def test_authentication_success(self):
        """Test successful authentication."""
        result = self.auth.authenticate("test@example.com", "password", "123456")
        self.assertTrue(result["success"])
        self.assertIn("session_token", result)
    
    def test_authentication_without_mfa(self):
        """Test authentication without MFA token."""
        result = self.auth.authenticate("test@example.com", "password")
        self.assertFalse(result["success"])
        self.assertTrue(result.get("mfa_required", False))
    
    def test_session_validation(self):
        """Test session token validation."""
        # Authenticate and get token
        result = self.auth.authenticate("test@example.com", "password", "123456")
        token = result["session_token"]
        
        # Validate token
        self.assertTrue(self.auth.validate_session(token))
        
        # Invalid token
        self.assertFalse(self.auth.validate_session("invalid_token"))
    
    def test_authorization(self):
        """Test resource authorization."""
        # Authenticate
        result = self.auth.authenticate("test@example.com", "password", "123456")
        token = result["session_token"]
        
        # Test authorization
        self.assertTrue(self.auth.authorize(token, "resource", "read"))
    
    def test_logout(self):
        """Test session logout."""
        # Authenticate
        result = self.auth.authenticate("test@example.com", "password", "123456")
        token = result["session_token"]
        
        # Logout
        self.assertTrue(self.auth.logout(token))
        
        # Token should be invalid after logout
        self.assertFalse(self.auth.validate_session(token))
    
    def test_account_lockout(self):
        """Test account lockout after failed attempts."""
        username = "lockout@example.com"
        
        # Record failed attempts
        for i in range(3):
            self.auth._record_failed_attempt(username)
        
        # Account should be locked
        self.assertTrue(self.auth._is_account_locked(username))


if __name__ == "__main__":
    unittest.main()
