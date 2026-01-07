"""
Authentication Module for SESF

Provides multi-factor authentication and authorization capabilities
for Starlink enterprise infrastructure.
"""

import hashlib
import secrets
from typing import Dict, Optional, List
from datetime import datetime, timedelta


class AuthenticationModule:
    """
    Handles authentication and authorization for SESF.
    
    Supports multi-factor authentication, session management,
    and role-based access control.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize authentication module.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.sessions = {}
        self.users = {}
        self.failed_attempts = {}
        self.max_attempts = self.config.get("max_login_attempts", 3)
        self.session_timeout = self.config.get("session_timeout", 3600)
    
    def authenticate(self, username: str, password: str, mfa_token: Optional[str] = None) -> Dict:
        """
        Authenticate a user with credentials.
        
        Args:
            username: User identifier
            password: User password
            mfa_token: Multi-factor authentication token
            
        Returns:
            Dict with authentication result and session token if successful
        """
        # Check if account is locked
        if self._is_account_locked(username):
            return {
                "success": False,
                "message": "Account locked due to too many failed attempts"
            }
        
        # Validate credentials (simplified for demo)
        if self._validate_credentials(username, password):
            # Check MFA if required
            if self.config.get("method") == "multi-factor" and not mfa_token:
                return {
                    "success": False,
                    "message": "MFA token required",
                    "mfa_required": True
                }
            
            if mfa_token and not self._validate_mfa(username, mfa_token):
                self._record_failed_attempt(username)
                return {
                    "success": False,
                    "message": "Invalid MFA token"
                }
            
            # Create session
            session_token = self._create_session(username)
            self._clear_failed_attempts(username)
            
            return {
                "success": True,
                "session_token": session_token,
                "expires_at": (datetime.now() + timedelta(seconds=self.session_timeout)).isoformat()
            }
        else:
            self._record_failed_attempt(username)
            return {
                "success": False,
                "message": "Invalid credentials"
            }
    
    def validate_session(self, session_token: str) -> bool:
        """
        Validate if a session token is still valid.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            bool: True if session is valid
        """
        if session_token not in self.sessions:
            return False
        
        session = self.sessions[session_token]
        if datetime.now() > session["expires_at"]:
            del self.sessions[session_token]
            return False
        
        return True
    
    def authorize(self, session_token: str, resource: str, permission: str) -> bool:
        """
        Check if user has permission to access a resource.
        
        Args:
            session_token: User's session token
            resource: Resource identifier
            permission: Required permission (read, write, admin)
            
        Returns:
            bool: True if authorized
        """
        if not self.validate_session(session_token):
            return False
        
        session = self.sessions[session_token]
        user_role = session.get("role", "user")
        
        # Role-based access control (simplified)
        role_permissions = {
            "admin": ["read", "write", "delete", "admin"],
            "operator": ["read", "write"],
            "user": ["read"]
        }
        
        return permission in role_permissions.get(user_role, [])
    
    def logout(self, session_token: str) -> bool:
        """
        Invalidate a session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            bool: True if session was invalidated
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials (simplified implementation)."""
        # In production, this would check against a secure database
        return True  # Placeholder for demo
    
    def _validate_mfa(self, username: str, token: str) -> bool:
        """Validate MFA token (simplified implementation)."""
        # In production, this would validate TOTP/SMS/hardware token
        return True  # Placeholder for demo
    
    def _create_session(self, username: str) -> str:
        """Create a new session for authenticated user."""
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            "username": username,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=self.session_timeout),
            "role": "user"  # Would be fetched from user database
        }
        return session_token
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts."""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        if attempts["count"] >= self.max_attempts:
            # Check if lockout period has expired (30 minutes)
            if datetime.now() < attempts["locked_until"]:
                return True
            else:
                self._clear_failed_attempts(username)
        
        return False
    
    def _record_failed_attempt(self, username: str):
        """Record a failed login attempt."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {
                "count": 0,
                "locked_until": None
            }
        
        self.failed_attempts[username]["count"] += 1
        
        if self.failed_attempts[username]["count"] >= self.max_attempts:
            self.failed_attempts[username]["locked_until"] = datetime.now() + timedelta(minutes=30)
    
    def _clear_failed_attempts(self, username: str):
        """Clear failed login attempts for user."""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
