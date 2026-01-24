"""Tests for encryption module."""


import pytest

from secure_it_infra.encryption import EncryptionManager, EncryptionError


class TestEncryptionManager:
    """Test cases for EncryptionManager class."""
    
    def test_create_manager_with_generated_key(self):
        """Test creating manager with auto-generated key."""
        manager = EncryptionManager()
        assert manager.key is not None
        assert len(manager.key) > 0
    
    def test_create_manager_with_custom_key(self):
        """Test creating manager with custom key."""
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        manager = EncryptionManager(key=key)
        assert manager.key == key
    
    def test_from_password(self):
        """Test creating manager from password."""
        manager = EncryptionManager.from_password("test_password")
        assert manager.key is not None
        assert manager.salt is not None
        assert len(manager.salt) == 16
    
    def test_from_password_with_salt(self):
        """Test creating manager from password with custom salt."""
        import os
        salt = os.urandom(16)
        manager = EncryptionManager.from_password("test_password", salt=salt)
        assert manager.salt == salt
    
    def test_from_password_bytes(self):
        """Test creating manager from password as bytes."""
        manager = EncryptionManager.from_password(b"test_password")
        assert manager.key is not None
    
    def test_encrypt_decrypt_bytes(self):
        """Test encrypting and decrypting bytes."""
        manager = EncryptionManager()
        data = b"sensitive data"
        
        encrypted = manager.encrypt(data)
        assert encrypted != data
        
        decrypted = manager.decrypt(encrypted)
        assert decrypted == data
    
    def test_encrypt_decrypt_string(self):
        """Test encrypting and decrypting string."""
        manager = EncryptionManager()
        data = "sensitive string data"
        
        encrypted = manager.encrypt(data)
        assert isinstance(encrypted, bytes)
        
        decrypted = manager.decrypt(encrypted)
        assert decrypted.decode() == data
    
    def test_encrypt_str_decrypt_str(self):
        """Test string-based encrypt/decrypt methods."""
        manager = EncryptionManager()
        data = "sensitive information"
        
        encrypted = manager.encrypt_str(data)
        assert isinstance(encrypted, str)
        assert encrypted != data
        
        decrypted = manager.decrypt_str(encrypted)
        assert decrypted == data
    
    def test_decrypt_with_wrong_key_raises_error(self):
        """Test that decrypting with wrong key raises error."""
        manager1 = EncryptionManager()
        manager2 = EncryptionManager()
        
        data = b"secret data"
        encrypted = manager1.encrypt(data)
        
        with pytest.raises(EncryptionError):
            manager2.decrypt(encrypted)
    
    def test_decrypt_str_with_invalid_data_raises_error(self):
        """Test that decrypting invalid data raises error."""
        manager = EncryptionManager()
        
        with pytest.raises(EncryptionError):
            manager.decrypt_str("invalid_encrypted_data")
    
    def test_same_password_different_salt_different_keys(self):
        """Test that same password with different salts produces different keys."""
        manager1 = EncryptionManager.from_password("password")
        manager2 = EncryptionManager.from_password("password")
        
        # Different salts should produce different keys
        assert manager1.salt != manager2.salt
        assert manager1.key != manager2.key
    
    def test_same_password_same_salt_same_key(self):
        """Test that same password and salt produces same key."""
        import os
        salt = os.urandom(16)
        
        manager1 = EncryptionManager.from_password("password", salt=salt)
        manager2 = EncryptionManager.from_password("password", salt=salt)
        
        assert manager1.key == manager2.key
    
    def test_rotate_key(self):
        """Test key rotation."""
        manager = EncryptionManager()
        old_key = manager.key
        
        returned_old_key = manager.rotate_key()
        assert returned_old_key == old_key
        assert manager.key != old_key
    
    def test_rotate_key_with_custom_key(self):
        """Test key rotation with custom new key."""
        from cryptography.fernet import Fernet
        
        manager = EncryptionManager()
        new_key = Fernet.generate_key()
        
        manager.rotate_key(new_key)
        assert manager.key == new_key
    
    def test_rotate_key_clears_salt(self):
        """Test that key rotation clears password-derived salt."""
        manager = EncryptionManager.from_password("password")
        assert manager.salt is not None
        
        manager.rotate_key()
        assert manager.salt is None
    
    def test_data_encrypted_before_rotation_cannot_decrypt_after(self):
        """Test that old encrypted data cannot be decrypted after key rotation."""
        manager = EncryptionManager()
        data = b"important data"
        
        encrypted = manager.encrypt(data)
        manager.rotate_key()
        
        with pytest.raises(EncryptionError):
            manager.decrypt(encrypted)
    
    def test_re_encrypt(self):
        """Test re-encrypting data with a new key."""
        from cryptography.fernet import Fernet
        
        manager = EncryptionManager()
        data = b"data to re-encrypt"
        
        encrypted_old = manager.encrypt(data)
        
        new_key = Fernet.generate_key()
        encrypted_new = manager.re_encrypt(encrypted_old, new_key)
        
        # Old manager cannot decrypt new encryption
        with pytest.raises(EncryptionError):
            manager.decrypt(encrypted_new)
        
        # New manager can decrypt
        new_manager = EncryptionManager(new_key)
        decrypted = new_manager.decrypt(encrypted_new)
        assert decrypted == data
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        manager = EncryptionManager()
        data = ""
        
        encrypted = manager.encrypt_str(data)
        decrypted = manager.decrypt_str(encrypted)
        
        assert decrypted == data
    
    def test_encrypt_unicode_string(self):
        """Test encrypting unicode string."""
        manager = EncryptionManager()
        data = "Hello 世界 🌍"
        
        encrypted = manager.encrypt_str(data)
        decrypted = manager.decrypt_str(encrypted)
        
        assert decrypted == data
    
    def test_encrypt_large_data(self):
        """Test encrypting large data."""
        manager = EncryptionManager()
        data = "x" * 1000000  # 1MB of data
        
        encrypted = manager.encrypt_str(data)
        decrypted = manager.decrypt_str(encrypted)
        
        assert decrypted == data


class TestEncryptionError:
    """Test cases for EncryptionError exception."""
    
    def test_encryption_error_is_exception(self):
        """Test that EncryptionError is an Exception."""
        assert issubclass(EncryptionError, Exception)
    
    def test_raise_encryption_error(self):
        """Test raising EncryptionError."""
        with pytest.raises(EncryptionError) as exc_info:
            raise EncryptionError("Test error message")
        
        assert str(exc_info.value) == "Test error message"
