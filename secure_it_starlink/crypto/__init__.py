"""
Encryption and Key Management Module
=====================================

Provides encryption utilities and key management for securing data
in Starlink-connected infrastructures.
"""

import os
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class EncryptionManager:
    """
    Manage encryption and decryption operations.
    
    Provides symmetric encryption for securing sensitive data in transit
    and at rest.
    """

    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize the Encryption Manager.
        
        Args:
            key: Optional encryption key. If not provided, a new key is generated.
        """
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.operations_log: list[Dict[str, Any]] = []

    def encrypt(self, data: str) -> str:
        """
        Encrypt data.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Base64-encoded encrypted data
        """
        encrypted = self.cipher.encrypt(data.encode())
        self.operations_log.append({
            "timestamp": datetime.now().isoformat(),
            "operation": "encrypt",
            "data_length": len(data)
        })
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            
        Returns:
            Decrypted plain text data
        """
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        self.operations_log.append({
            "timestamp": datetime.now().isoformat(),
            "operation": "decrypt",
            "data_length": len(decrypted)
        })
        return decrypted.decode()

    def get_key(self) -> str:
        """
        Get the encryption key.
        
        Returns:
            Base64-encoded encryption key
        """
        return self.key.decode()

    def rotate_key(self, new_key: Optional[bytes] = None) -> str:
        """
        Rotate the encryption key.
        
        Args:
            new_key: Optional new key. If not provided, a new key is generated.
            
        Returns:
            Base64-encoded new encryption key
        """
        old_key = self.key
        self.key = new_key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        
        self.operations_log.append({
            "timestamp": datetime.now().isoformat(),
            "operation": "key_rotation",
            "old_key_length": len(old_key),
            "new_key_length": len(self.key)
        })
        
        return self.key.decode()

    def get_operations_log(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        """
        Get encryption operations log.
        
        Args:
            limit: Maximum number of log entries to return
            
        Returns:
            List of operation log entries
        """
        if limit:
            return self.operations_log[-limit:]
        return self.operations_log.copy()


class KeyManager:
    """
    Manage cryptographic keys for the infrastructure.
    
    Provides key generation, storage, rotation, and lifecycle management.
    """

    def __init__(self, master_password: Optional[str] = None):
        """
        Initialize the Key Manager.
        
        Args:
            master_password: Optional master password for key derivation
        """
        self.master_password = master_password
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.key_rotation_days = 90

    def generate_key(self, key_id: str, key_type: str = "symmetric") -> Dict[str, Any]:
        """
        Generate a new cryptographic key.
        
        Args:
            key_id: Unique identifier for the key
            key_type: Type of key to generate (symmetric, asymmetric)
            
        Returns:
            Dictionary containing key information
        """
        if key_type == "symmetric":
            key = Fernet.generate_key()
            key_data = {
                "key_id": key_id,
                "key_type": key_type,
                "key": key.decode(),
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=self.key_rotation_days)).isoformat(),
                "status": "active"
            }
        else:
            raise NotImplementedError(f"Key type '{key_type}' not yet implemented")

        self.keys[key_id] = key_data
        return key_data

    def get_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a key by ID.
        
        Args:
            key_id: Key identifier
            
        Returns:
            Key information dictionary or None if not found
        """
        return self.keys.get(key_id)

    def rotate_key(self, key_id: str) -> Dict[str, Any]:
        """
        Rotate an existing key.
        
        Args:
            key_id: Key identifier to rotate
            
        Returns:
            New key information dictionary
        """
        if key_id not in self.keys:
            raise ValueError(f"Key '{key_id}' not found")

        old_key = self.keys[key_id]
        old_key["status"] = "rotated"
        old_key["rotated_at"] = datetime.now().isoformat()

        new_key_data = self.generate_key(key_id, old_key["key_type"])
        return new_key_data

    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke a key.
        
        Args:
            key_id: Key identifier to revoke
            
        Returns:
            True if key was revoked, False otherwise
        """
        if key_id in self.keys:
            self.keys[key_id]["status"] = "revoked"
            self.keys[key_id]["revoked_at"] = datetime.now().isoformat()
            return True
        return False

    def list_keys(self, status: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        List all keys, optionally filtered by status.
        
        Args:
            status: Optional status filter (active, rotated, revoked)
            
        Returns:
            List of key information dictionaries
        """
        if status:
            return [key for key in self.keys.values() if key["status"] == status]
        return list(self.keys.values())

    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive a key from a password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Optional salt. If not provided, a random salt is generated.
            
        Returns:
            Derived key bytes
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key)
