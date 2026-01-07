"""
Access Control and Authentication Module
=========================================

Provides access control, authentication, and authorization for
Starlink-connected infrastructures.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class AccessController:
    """
    Control access to infrastructure resources.
    
    Manages access policies, permissions, and resource access control.
    """

    def __init__(self):
        """Initialize the Access Controller."""
        self.access_policies: Dict[str, Dict[str, Any]] = {}
        self.access_logs: List[Dict[str, Any]] = []
        self.resources: Dict[str, Dict[str, Any]] = {}

    def create_policy(
        self,
        policy_id: str,
        resource: str,
        allowed_actions: List[str],
        principals: List[str]
    ) -> Dict[str, Any]:
        """
        Create an access control policy.
        
        Args:
            policy_id: Unique policy identifier
            resource: Resource identifier
            allowed_actions: List of allowed actions
            principals: List of principal identifiers (users, roles, etc.)
            
        Returns:
            Created policy
        """
        policy = {
            "policy_id": policy_id,
            "resource": resource,
            "allowed_actions": allowed_actions,
            "principals": principals,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }

        self.access_policies[policy_id] = policy
        return policy

    def check_access(
        self,
        principal: str,
        resource: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Check if access is allowed.
        
        Args:
            principal: Principal identifier
            resource: Resource identifier
            action: Requested action
            
        Returns:
            Access decision with details
        """
        access_decision = {
            "principal": principal,
            "resource": resource,
            "action": action,
            "allowed": False,
            "timestamp": datetime.now().isoformat(),
            "matched_policies": []
        }

        for policy_id, policy in self.access_policies.items():
            if policy["status"] != "active":
                continue

            if (resource == policy["resource"] and
                action in policy["allowed_actions"] and
                principal in policy["principals"]):
                access_decision["allowed"] = True
                access_decision["matched_policies"].append(policy_id)

        self.access_logs.append(access_decision)
        return access_decision

    def revoke_policy(self, policy_id: str) -> bool:
        """
        Revoke an access policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            True if policy was revoked, False otherwise
        """
        if policy_id in self.access_policies:
            self.access_policies[policy_id]["status"] = "revoked"
            self.access_policies[policy_id]["revoked_at"] = datetime.now().isoformat()
            return True
        return False

    def get_policies(self, resource: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get access policies, optionally filtered by resource.
        
        Args:
            resource: Optional resource filter
            
        Returns:
            List of policies
        """
        policies = list(self.access_policies.values())
        if resource:
            policies = [p for p in policies if p["resource"] == resource]
        return policies

    def get_access_logs(
        self,
        principal: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get access logs.
        
        Args:
            principal: Optional principal filter
            limit: Maximum number of logs to return
            
        Returns:
            List of access log entries
        """
        logs = self.access_logs
        if principal:
            logs = [log for log in logs if log["principal"] == principal]

        if limit:
            return logs[-limit:]
        return logs.copy()


class AuthenticationManager:
    """
    Manage user authentication and sessions.
    
    Handles user credentials, authentication, and session management.
    """

    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize the Authentication Manager.
        
        Args:
            session_timeout_minutes: Session timeout in minutes
        """
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.auth_logs: List[Dict[str, Any]] = []

    def create_user(
        self,
        username: str,
        password: str,
        roles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            username: Username
            password: Plain text password (will be hashed)
            roles: Optional list of roles
            
        Returns:
            Created user information (without password hash)
        """
        if username in self.users:
            raise ValueError(f"User '{username}' already exists")

        password_hash = self._hash_password(password)
        
        user = {
            "username": username,
            "password_hash": password_hash,
            "roles": roles or [],
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "failed_login_attempts": 0
        }

        self.users[username] = user

        return {
            "username": username,
            "roles": roles or [],
            "created_at": user["created_at"],
            "status": user["status"]
        }

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate a user and create a session.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Session token if authentication successful, None otherwise
        """
        auth_log = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "success": False
        }

        if username not in self.users:
            auth_log["reason"] = "user_not_found"
            self.auth_logs.append(auth_log)
            return None

        user = self.users[username]

        if user["status"] != "active":
            auth_log["reason"] = "user_inactive"
            self.auth_logs.append(auth_log)
            return None

        password_hash = self._hash_password(password)
        if password_hash != user["password_hash"]:
            user["failed_login_attempts"] += 1
            auth_log["reason"] = "invalid_password"
            self.auth_logs.append(auth_log)
            return None

        # Reset failed attempts on successful login
        user["failed_login_attempts"] = 0
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        session = {
            "session_token": session_token,
            "username": username,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + self.session_timeout,
            "status": "active"
        }

        self.sessions[session_token] = session
        auth_log["success"] = True
        self.auth_logs.append(auth_log)

        return session_token

    def validate_session(self, session_token: str) -> Optional[str]:
        """
        Validate a session token.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            Username if session is valid, None otherwise
        """
        if session_token not in self.sessions:
            return None

        session = self.sessions[session_token]

        if session["status"] != "active":
            return None

        if datetime.now() > session["expires_at"]:
            session["status"] = "expired"
            return None

        # Extend session on valid access
        session["expires_at"] = datetime.now() + self.session_timeout

        return session["username"]

    def logout(self, session_token: str) -> bool:
        """
        Logout a session.
        
        Args:
            session_token: Session token
            
        Returns:
            True if logout successful, False otherwise
        """
        if session_token in self.sessions:
            self.sessions[session_token]["status"] = "logged_out"
            self.sessions[session_token]["logged_out_at"] = datetime.now()
            return True
        return False

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information (without password hash).
        
        Args:
            username: Username
            
        Returns:
            User information or None
        """
        if username not in self.users:
            return None

        user = self.users[username].copy()
        user.pop("password_hash", None)
        return user

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_auth_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get authentication logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of authentication log entries
        """
        if limit:
            return self.auth_logs[-limit:]
        return self.auth_logs.copy()
