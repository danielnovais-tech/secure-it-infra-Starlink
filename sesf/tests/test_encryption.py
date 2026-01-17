"""
Unit tests for SESF Encryption Module
"""

import unittest
from sesf.modules.encryption import EncryptionModule


class TestEncryptionModule(unittest.TestCase):
    """Test cases for EncryptionModule."""
    
    def setUp(self):
        """Set up test encryption module."""
        self.encryption = EncryptionModule({
            "encryption_algorithm": "AES-256-GCM"
        })
    
    def test_key_generation(self):
        """Test encryption key generation."""
        key_id = self.encryption.generate_key()
        self.assertIsNotNone(key_id)
        self.assertIn(key_id, self.encryption.keys)
    
    def test_encryption(self):
        """Test data encryption."""
        data = b"Test data for encryption"
        result = self.encryption.encrypt(data)
        
        self.assertIn("encrypted_data", result)
        self.assertIn("key_id", result)
        self.assertIn("nonce", result)
        self.assertEqual(result["algorithm"], "AES-256-GCM")
    
    def test_decryption(self):
        """Test data decryption."""
        data = b"Test data for encryption"
        
        # Encrypt
        encrypted = self.encryption.encrypt(data)
        
        # Decrypt
        decrypted = self.encryption.decrypt(
            encrypted["encrypted_data"],
            encrypted["key_id"],
            encrypted["nonce"]
        )
        
        self.assertEqual(decrypted, data)
    
    def test_key_rotation(self):
        """Test key rotation."""
        # Generate some keys
        self.encryption.generate_key("key1")
        self.encryption.generate_key("key2")
        
        # Rotate keys
        result = self.encryption.rotate_keys()
        
        self.assertEqual(result["rotated_keys"], 2)
        self.assertIn("key_mapping", result)
    
    def test_secure_channel_creation(self):
        """Test secure channel creation."""
        channel = self.encryption.create_secure_channel("remote-endpoint-1")
        
        self.assertIn("channel_id", channel)
        self.assertIn("key_id", channel)
        self.assertEqual(channel["remote_id"], "remote-endpoint-1")
    
    def test_hash_data(self):
        """Test data hashing."""
        data = b"Test data to hash"
        
        # SHA-256
        hash_256 = self.encryption.hash_data(data, "sha256")
        self.assertEqual(len(hash_256), 64)  # SHA-256 produces 64 hex chars
        
        # SHA-512
        hash_512 = self.encryption.hash_data(data, "sha512")
        self.assertEqual(len(hash_512), 128)  # SHA-512 produces 128 hex chars
    
    def test_get_key_status(self):
        """Test getting key status."""
        key_id = self.encryption.generate_key()
        status = self.encryption.get_key_status(key_id)
        
        self.assertIsNotNone(status)
        assert status is not None
        self.assertEqual(status["key_id"], key_id)
        self.assertIn("created_at", status)
        self.assertIn("usage_count", status)


if __name__ == "__main__":
    unittest.main()

