"""
Test encryption and decryption operations for confidential MPT.

This module tests:
- ElGamal keypair generation
- ElGamal encryption
- ElGamal decryption
- Round-trip encryption/decryption
"""

import secrets
import unittest

from xrpl.core.confidential import MPTCrypto


class TestEncryption(unittest.TestCase):
    """Test ElGamal encryption and decryption."""

    def setUp(self):
        """Set up test fixtures."""
        self.crypto = MPTCrypto()

    def test_generate_keypair(self):
        """Test ElGamal keypair generation."""
        privkey, pubkey = self.crypto.generate_keypair()

        # Check sizes
        self.assertEqual(len(privkey), 64)  # 32 bytes = 64 hex chars
        self.assertEqual(len(pubkey), 128)  # 64 bytes = 128 hex chars

        # Check they're valid hex
        bytes.fromhex(privkey)
        bytes.fromhex(pubkey)

    def test_generate_keypair_uniqueness(self):
        """Test that keypair generation produces unique keys."""
        privkey1, pubkey1 = self.crypto.generate_keypair()
        privkey2, pubkey2 = self.crypto.generate_keypair()

        self.assertNotEqual(privkey1, privkey2)
        self.assertNotEqual(pubkey1, pubkey2)

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption round-trip."""
        # Generate keypair
        privkey, pubkey = self.crypto.generate_keypair()

        # Test various amounts (note: very large values may fail due to discrete log)
        test_amounts = [0, 1, 100, 1000, 10000, 1000000]

        for amount in test_amounts:
            with self.subTest(amount=amount):
                # Encrypt
                c1, c2, blinding = self.crypto.encrypt(pubkey, amount)

                # Check sizes
                self.assertEqual(len(c1), 66)  # 33 bytes = 66 hex chars
                self.assertEqual(len(c2), 66)  # 33 bytes = 66 hex chars
                self.assertEqual(len(blinding), 64)  # 32 bytes = 64 hex chars

                # Decrypt
                decrypted_amount = self.crypto.decrypt(privkey, c1, c2)

                # Verify round-trip
                self.assertEqual(decrypted_amount, amount)

    def test_encrypt_with_custom_blinding(self):
        """Test encryption with a custom blinding factor."""
        privkey, pubkey = self.crypto.generate_keypair()
        amount = 12345

        # Use custom blinding factor
        custom_blinding = secrets.token_bytes(32).hex().upper()

        c1, c2, returned_blinding = self.crypto.encrypt(pubkey, amount, custom_blinding)

        # Verify the blinding factor is the one we provided
        self.assertEqual(returned_blinding, custom_blinding)

        # Verify decryption still works
        decrypted_amount = self.crypto.decrypt(privkey, c1, c2)
        self.assertEqual(decrypted_amount, amount)

    def test_encrypt_same_amount_different_ciphertexts(self):
        """Test that encrypting the same amount produces different ciphertexts."""
        privkey, pubkey = self.crypto.generate_keypair()
        amount = 1000

        # Encrypt twice (with random blinding factors)
        c1_a, c2_a, blinding_a = self.crypto.encrypt(pubkey, amount)
        c1_b, c2_b, blinding_b = self.crypto.encrypt(pubkey, amount)

        # Ciphertexts should be different (probabilistic encryption)
        self.assertNotEqual(c1_a, c1_b)
        self.assertNotEqual(c2_a, c2_b)
        self.assertNotEqual(blinding_a, blinding_b)

        # But both should decrypt to the same amount
        decrypted_a = self.crypto.decrypt(privkey, c1_a, c2_a)
        decrypted_b = self.crypto.decrypt(privkey, c1_b, c2_b)
        self.assertEqual(decrypted_a, amount)
        self.assertEqual(decrypted_b, amount)

    def test_encrypt_for_multiple_recipients(self):
        """Test encrypting the same amount for multiple recipients."""
        # Generate keypairs for 3 recipients
        recipients = [self.crypto.generate_keypair() for _ in range(3)]
        amount = 5000

        # Use the same blinding factor for all
        blinding = secrets.token_bytes(32).hex().upper()

        # Encrypt for each recipient
        ciphertexts = []
        for privkey, pubkey in recipients:
            c1, c2, _ = self.crypto.encrypt(pubkey, amount, blinding)
            ciphertexts.append((privkey, c1, c2))

        # Each recipient should be able to decrypt
        for privkey, c1, c2 in ciphertexts:
            decrypted = self.crypto.decrypt(privkey, c1, c2)
            self.assertEqual(decrypted, amount)

    def test_decrypt_with_wrong_key(self):
        """Test that decryption with wrong key fails or produces wrong result."""
        # Generate two keypairs
        privkey1, pubkey1 = self.crypto.generate_keypair()
        privkey2, _ = self.crypto.generate_keypair()

        amount = 1000

        # Encrypt for recipient 1
        c1, c2, _ = self.crypto.encrypt(pubkey1, amount)

        # Decrypt with correct key
        decrypted_correct = self.crypto.decrypt(privkey1, c1, c2)
        self.assertEqual(decrypted_correct, amount)

        # Decrypt with wrong key should fail (raises RuntimeError)
        with self.assertRaises(RuntimeError):
            self.crypto.decrypt(privkey2, c1, c2)


if __name__ == "__main__":
    unittest.main()
