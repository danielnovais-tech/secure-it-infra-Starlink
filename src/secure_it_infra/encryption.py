"""Encryption management for sensitive data."""

import base64
import os
from typing import Optional, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """Manages encryption and decryption of sensitive data.
    
    This class provides encryption services using Fernet symmetric encryption
    with support for key derivation from passwords.
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """Initialize the encryption manager.
        
        Args:
            key: Encryption key (32 url-safe base64-encoded bytes).
                 If None, a new key is generated.
        """
        self._salt: Optional[bytes] = None
        if key is None:
            key = Fernet.generate_key()
        self._fernet: Fernet = Fernet(key)
        self._key: bytes = key
    
    @classmethod
    def from_password(
        cls,
        password: Union[str, bytes],
        salt: Optional[bytes] = None
    ) -> "EncryptionManager":
        """Create an EncryptionManager from a password.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (16 bytes recommended).
                  If None, a new salt is generated.
                  
        Returns:
            New EncryptionManager instance
        """
        if isinstance(password, str):
            password = password.encode()
        
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        manager = cls(key)
        manager._salt = salt
        return manager
    
    @property
    def key(self) -> bytes:
        """Get the encryption key.
        
        Returns:
            Encryption key as bytes
        """
        return self._key
    
    @property
    def salt(self) -> Optional[bytes]:
        """Get the salt used for key derivation.
        
        Returns:
            Salt bytes if key was derived from password, None otherwise
        """
        return self._salt
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """Encrypt data.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Encrypted data as bytes
        """
        if isinstance(data, str):
            data = data.encode()
        return self._fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Decrypted data as bytes
            
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            return self._fernet.decrypt(encrypted_data)
        except InvalidToken as e:
            raise EncryptionError("Failed to decrypt data: invalid key or corrupted data") from e
    
    def encrypt_str(self, data: str) -> str:
        """Encrypt a string and return base64-encoded result.
        
        Args:
            data: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        encrypted = self.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_str(self, encrypted_data: str) -> str:
        """Decrypt a base64-encoded encrypted string.
        
        Args:
            encrypted_data: Base64-encoded encrypted string
            
        Returns:
            Decrypted string
            
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt string: {str(e)}") from e
    
    def rotate_key(self, new_key: Optional[bytes] = None) -> bytes:
        """Rotate the encryption key.
        
        Args:
            new_key: New encryption key. If None, generates a new key.
            
        Returns:
            The old encryption key
            
        Note:
            After rotating the key, previously encrypted data cannot be
            decrypted with the new manager. You should decrypt and
            re-encrypt data with the new key.
        """
        old_key = self._key
        
        if new_key is None:
            new_key = Fernet.generate_key()
        
        self._key = new_key
        self._fernet = Fernet(new_key)
        
        # Clear salt if it exists since key is no longer password-derived
        self._salt = None
        
        return old_key
    
    def re_encrypt(self, encrypted_data: bytes, new_key: bytes) -> bytes:
        """Re-encrypt data with a new key.
        
        Args:
            encrypted_data: Data encrypted with current key
            new_key: New key to encrypt with
            
        Returns:
            Data encrypted with new key
            
        Raises:
            EncryptionError: If decryption or encryption fails
        """
        # Decrypt with current key
        decrypted = self.decrypt(encrypted_data)
        
        # Create new manager with new key
        new_manager = EncryptionManager(new_key)
        
        # Encrypt with new key
        return new_manager.encrypt(decrypted)


class EncryptionError(Exception):
    """Exception raised for encryption-related errors."""
    pass
