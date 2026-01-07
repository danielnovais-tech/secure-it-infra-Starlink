"""Tests for the encryption and key management module."""

import pytest
from secure_it_starlink.crypto import EncryptionManager, KeyManager


class TestEncryptionManager:
    """Test the EncryptionManager class."""

    def test_initialization(self):
        """Test encryption manager initialization."""
        manager = EncryptionManager()
        assert manager.key is not None
        assert manager.cipher is not None
        assert len(manager.operations_log) == 0

    def test_encrypt_decrypt(self):
        """Test encryption and decryption."""
        manager = EncryptionManager()
        plaintext = "This is a test message"
        
        # Encrypt
        encrypted = manager.encrypt(plaintext)
        assert encrypted != plaintext
        assert len(manager.operations_log) == 1
        
        # Decrypt
        decrypted = manager.decrypt(encrypted)
        assert decrypted == plaintext
        assert len(manager.operations_log) == 2

    def test_get_key(self):
        """Test getting encryption key."""
        manager = EncryptionManager()
        key = manager.get_key()
        assert isinstance(key, str)
        assert len(key) > 0

    def test_rotate_key(self):
        """Test key rotation."""
        manager = EncryptionManager()
        old_key = manager.get_key()
        
        new_key = manager.rotate_key()
        assert new_key != old_key
        assert manager.get_key() == new_key

    def test_operations_log(self):
        """Test operations logging."""
        manager = EncryptionManager()
        manager.encrypt("test1")
        manager.encrypt("test2")
        
        logs = manager.get_operations_log()
        assert len(logs) == 2
        
        # Test with limit
        limited_logs = manager.get_operations_log(limit=1)
        assert len(limited_logs) == 1


class TestKeyManager:
    """Test the KeyManager class."""

    def test_initialization(self):
        """Test key manager initialization."""
        manager = KeyManager()
        assert len(manager.keys) == 0

    def test_generate_key(self):
        """Test key generation."""
        manager = KeyManager()
        key_data = manager.generate_key("test-key", "symmetric")
        
        assert key_data["key_id"] == "test-key"
        assert key_data["key_type"] == "symmetric"
        assert "key" in key_data
        assert "created_at" in key_data
        assert "expires_at" in key_data
        assert key_data["status"] == "active"

    def test_get_key(self):
        """Test retrieving a key."""
        manager = KeyManager()
        manager.generate_key("test-key", "symmetric")
        
        key_data = manager.get_key("test-key")
        assert key_data is not None
        assert key_data["key_id"] == "test-key"
        
        # Test non-existent key
        assert manager.get_key("non-existent") is None

    def test_rotate_key(self):
        """Test key rotation."""
        manager = KeyManager()
        manager.generate_key("test-key", "symmetric")
        old_key = manager.get_key("test-key")["key"]
        
        new_key_data = manager.rotate_key("test-key")
        assert new_key_data["key"] != old_key
        assert new_key_data["status"] == "active"

    def test_rotate_nonexistent_key(self):
        """Test rotating non-existent key raises error."""
        manager = KeyManager()
        with pytest.raises(ValueError):
            manager.rotate_key("non-existent")

    def test_revoke_key(self):
        """Test key revocation."""
        manager = KeyManager()
        manager.generate_key("test-key", "symmetric")
        
        result = manager.revoke_key("test-key")
        assert result is True
        
        key_data = manager.get_key("test-key")
        assert key_data["status"] == "revoked"
        
        # Test revoking non-existent key
        assert manager.revoke_key("non-existent") is False

    def test_list_keys(self):
        """Test listing keys."""
        manager = KeyManager()
        manager.generate_key("key1", "symmetric")
        manager.generate_key("key2", "symmetric")
        manager.revoke_key("key2")
        
        all_keys = manager.list_keys()
        assert len(all_keys) == 2
        
        active_keys = manager.list_keys(status="active")
        assert len(active_keys) == 1
        
        revoked_keys = manager.list_keys(status="revoked")
        assert len(revoked_keys) == 1

    def test_derive_key_from_password(self):
        """Test key derivation from password."""
        manager = KeyManager()
        password = "SecureP@ssw0rd123"
        
        key1 = manager.derive_key_from_password(password)
        assert key1 is not None
        assert len(key1) > 0
