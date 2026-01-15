"""Tests for the access control and authentication module."""

import pytest
from secure_it_starlink.access import AccessController, AuthenticationManager


class TestAccessController:
    """Test the AccessController class."""

    def test_initialization(self):
        """Test access controller initialization."""
        controller = AccessController()
        assert len(controller.access_policies) == 0
        assert len(controller.access_logs) == 0

    def test_create_policy(self):
        """Test creating an access policy."""
        controller = AccessController()
        policy = controller.create_policy(
            "test-policy",
            resource="database",
            allowed_actions=["read", "write"],
            principals=["user1", "user2"]
        )
        
        assert policy["policy_id"] == "test-policy"
        assert policy["resource"] == "database"
        assert policy["allowed_actions"] == ["read", "write"]
        assert policy["principals"] == ["user1", "user2"]
        assert policy["status"] == "active"

    def test_check_access_allowed(self):
        """Test checking allowed access."""
        controller = AccessController()
        controller.create_policy(
            "test-policy",
            resource="database",
            allowed_actions=["read", "write"],
            principals=["user1"]
        )
        
        decision = controller.check_access("user1", "database", "read")
        
        assert decision["allowed"] is True
        assert decision["principal"] == "user1"
        assert decision["resource"] == "database"
        assert decision["action"] == "read"
        assert len(decision["matched_policies"]) == 1

    def test_check_access_denied(self):
        """Test checking denied access."""
        controller = AccessController()
        controller.create_policy(
            "test-policy",
            resource="database",
            allowed_actions=["read"],
            principals=["user1"]
        )
        
        # Wrong user
        decision = controller.check_access("user2", "database", "read")
        assert decision["allowed"] is False
        
        # Wrong action
        decision = controller.check_access("user1", "database", "delete")
        assert decision["allowed"] is False

    def test_revoke_policy(self):
        """Test revoking a policy."""
        controller = AccessController()
        controller.create_policy(
            "test-policy",
            resource="database",
            allowed_actions=["read"],
            principals=["user1"]
        )
        
        result = controller.revoke_policy("test-policy")
        assert result is True
        
        # Verify policy is revoked
        policies = controller.get_policies()
        assert policies[0]["status"] == "revoked"
        
        # Test revoking non-existent policy
        assert controller.revoke_policy("non-existent") is False

    def test_get_policies(self):
        """Test getting policies."""
        controller = AccessController()
        controller.create_policy("policy1", "resource1", ["read"], ["user1"])
        controller.create_policy("policy2", "resource2", ["write"], ["user2"])
        
        all_policies = controller.get_policies()
        assert len(all_policies) == 2
        
        # Test filtering by resource
        resource1_policies = controller.get_policies(resource="resource1")
        assert len(resource1_policies) == 1

    def test_get_access_logs(self):
        """Test getting access logs."""
        controller = AccessController()
        controller.create_policy("policy1", "resource1", ["read"], ["user1"])
        
        controller.check_access("user1", "resource1", "read")
        controller.check_access("user2", "resource1", "read")
        
        all_logs = controller.get_access_logs()
        assert len(all_logs) == 2
        
        # Test filtering by principal
        user1_logs = controller.get_access_logs(principal="user1")
        assert len(user1_logs) == 1
        
        # Test with limit
        limited_logs = controller.get_access_logs(limit=1)
        assert len(limited_logs) == 1


class TestAuthenticationManager:
    """Test the AuthenticationManager class."""

    def test_initialization(self):
        """Test authentication manager initialization."""
        manager = AuthenticationManager()
        assert len(manager.users) == 0
        assert len(manager.sessions) == 0

    def test_create_user(self):
        """Test creating a user."""
        manager = AuthenticationManager()
        user = manager.create_user("testuser", "SecureP@ss123", ["admin"])
        
        assert user["username"] == "testuser"
        assert user["roles"] == ["admin"]
        assert user["status"] == "active"
        assert "password_hash" not in user  # Should not expose hash

    def test_create_duplicate_user(self):
        """Test creating duplicate user raises error."""
        manager = AuthenticationManager()
        manager.create_user("testuser", "password")
        
        with pytest.raises(ValueError):
            manager.create_user("testuser", "password")

    def test_authenticate_success(self):
        """Test successful authentication."""
        manager = AuthenticationManager()
        manager.create_user("testuser", "SecureP@ss123")
        
        token = manager.authenticate("testuser", "SecureP@ss123")
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_authenticate_wrong_password(self):
        """Test authentication with wrong password."""
        manager = AuthenticationManager()
        manager.create_user("testuser", "SecureP@ss123")
        
        token = manager.authenticate("testuser", "WrongPassword")
        
        assert token is None

    def test_authenticate_nonexistent_user(self):
        """Test authentication with non-existent user."""
        manager = AuthenticationManager()
        
        token = manager.authenticate("nonexistent", "password")
        
        assert token is None

    def test_validate_session(self):
        """Test session validation."""
        manager = AuthenticationManager()
        manager.create_user("testuser", "SecureP@ss123")
        token = manager.authenticate("testuser", "SecureP@ss123")
        
        username = manager.validate_session(token)
        
        assert username == "testuser"
        
        # Test invalid token
        assert manager.validate_session("invalid-token") is None

    def test_logout(self):
        """Test logout."""
        manager = AuthenticationManager()
        manager.create_user("testuser", "SecureP@ss123")
        token = manager.authenticate("testuser", "SecureP@ss123")
        
        result = manager.logout(token)
        assert result is True
        
        # Verify session is logged out
        username = manager.validate_session(token)
        assert username is None
        
        # Test logging out non-existent session
        assert manager.logout("invalid-token") is False

    def test_get_user(self):
        """Test getting user information."""
        manager = AuthenticationManager()
        manager.create_user("testuser", "SecureP@ss123", ["admin"])
        
        user = manager.get_user("testuser")
        
        assert user is not None
        assert user["username"] == "testuser"
        assert user["roles"] == ["admin"]
        assert "password_hash" not in user
        
        # Test non-existent user
        assert manager.get_user("nonexistent") is None

    def test_get_auth_logs(self):
        """Test getting authentication logs."""
        manager = AuthenticationManager()
        manager.create_user("testuser", "SecureP@ss123")
        
        manager.authenticate("testuser", "SecureP@ss123")
        manager.authenticate("testuser", "WrongPassword")
        
        logs = manager.get_auth_logs()
        assert len(logs) == 2
        
        # Test with limit
        limited_logs = manager.get_auth_logs(limit=1)
        assert len(limited_logs) == 1

    def test_failed_login_attempts(self):
        """Test tracking failed login attempts."""
        manager = AuthenticationManager()
        manager.create_user("testuser", "SecureP@ss123")
        
        # Make failed attempts
        manager.authenticate("testuser", "wrong1")
        manager.authenticate("testuser", "wrong2")
        
        user = manager.users["testuser"]
        assert user["failed_login_attempts"] == 2
        
        # Successful login should reset counter
        manager.authenticate("testuser", "SecureP@ss123")
        assert user["failed_login_attempts"] == 0
