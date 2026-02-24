"""
Test suite for MPT utility layer functions.

This test suite mirrors the C++ tests in tools/mpt-crypto-mpt-utility/tests/test_mpt_utility.cpp
to ensure the Python wrappers correctly call the utility layer functions.
"""

import secrets
import unittest

from xrpl.core.confidential import (
    commitments,
    context,
    encryption,
    keypair,
    link_proofs,
    plaintext_proofs,
)
from xrpl.core.confidential.crypto_bindings import ffi, lib


def create_mock_account_id(fill_byte: int) -> str:
    """Create a mock 20-byte account ID filled with a specific byte as hex string."""
    return bytes([fill_byte] * 20).hex().upper()


def create_mock_issuance_id(fill_byte: int) -> str:
    """Create a mock 24-byte MPT issuance ID filled with a specific byte as hex string."""
    return bytes([fill_byte] * 24).hex().upper()


class TestEncryptionDecryption(unittest.TestCase):
    """Test encryption and decryption using utility layer (mirrors test_encryption_decryption)."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption/decryption for various amounts."""
        # Generate keypair
        privkey, pubkey = keypair.generate_keypair()

        # Test amounts (note: large numbers not supported yet due to discrete log limitation)
        test_amounts = [0, 1, 1000]

        for amount in test_amounts:
            with self.subTest(amount=amount):
                # Generate blinding factor
                blinding_factor = secrets.token_bytes(32).hex().upper()

                # Encrypt
                c1, c2, returned_bf = encryption.encrypt(None, pubkey, amount, blinding_factor)

                # Verify blinding factor is what we provided
                self.assertEqual(returned_bf, blinding_factor)

                # Decrypt
                decrypted_amount = encryption.decrypt(None, privkey, c1, c2)

                # Verify round-trip
                self.assertEqual(decrypted_amount, amount)


class TestConfidentialConvert(unittest.TestCase):
    """Test confidential convert transaction (mirrors test_mpt_confidential_convert)."""

    def test_convert_transaction(self):
        """Test generating convert proof and verifying encryption."""
        # Setup mock account, issuance and transaction details
        acc = create_mock_account_id(0xAA)
        issuance = create_mock_issuance_id(0xBB)
        seq = 12345
        convert_amount = 750

        # Generate keypair
        privkey, pubkey = keypair.generate_keypair()

        # Generate blinding factor and encrypt
        blinding_factor = secrets.token_bytes(32).hex().upper()
        c1, c2, _ = encryption.encrypt(None, pubkey, convert_amount, blinding_factor)

        # Generate context hash
        tx_hash = context.compute_convert_context_hash(
            acc,
            seq,
            issuance,
            convert_amount
        )

        # Generate convert proof (Schnorr proof of knowledge)
        proof = keypair.generate_pok(None, privkey, pubkey, tx_hash)

        # Verify proof length
        self.assertEqual(len(proof), 130)  # 65 bytes = 130 hex chars

        # Verify encryption using low-level secp256k1 functions
        ctx = lib.mpt_secp256k1_context()
        self.assertNotEqual(ctx, ffi.NULL)

        # Parse ciphertext components
        c1_bytes = bytes.fromhex(c1)
        c2_bytes = bytes.fromhex(c2)
        pubkey_bytes = bytes.fromhex(pubkey)
        bf_bytes = bytes.fromhex(blinding_factor)
        proof_bytes = bytes.fromhex(proof)
        tx_hash_bytes = bytes.fromhex(tx_hash)

        c1_pk = ffi.new("secp256k1_pubkey *")
        c2_pk = ffi.new("secp256k1_pubkey *")
        pk = ffi.new("secp256k1_pubkey *")

        # Parse compressed points
        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, c1_pk, c1_bytes, 33), 1)
        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, c2_pk, c2_bytes, 33), 1)
        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, pk, pubkey_bytes, 33), 1)

        # Verify encryption
        self.assertEqual(
            lib.secp256k1_elgamal_verify_encryption(ctx, c1_pk, c2_pk, pk, convert_amount, bf_bytes),
            1
        )

        # Verify Schnorr proof
        self.assertEqual(
            lib.secp256k1_mpt_pok_sk_verify(ctx, proof_bytes, pk, tx_hash_bytes),
            1
        )


class TestConfidentialSend(unittest.TestCase):
    """Test confidential send transaction (mirrors test_mpt_confidential_send)."""

    def test_send_transaction(self):
        """Test generating confidential send proof with multi-ciphertext equality and linkage proofs."""
        # Setup mock account, issuance and transaction details
        sender_acc = create_mock_account_id(0x11)
        dest_acc = create_mock_account_id(0x22)
        issuance = create_mock_issuance_id(0xBB)
        seq = 54321
        amount_to_send = 100
        prev_balance = 2000
        version = 1

        # Generate keypairs for all parties
        sender_priv, sender_pub = keypair.generate_keypair()
        dest_priv, dest_pub = keypair.generate_keypair()
        issuer_priv, issuer_pub = keypair.generate_keypair()

        # Encrypt for all recipients using same shared blinding factor
        shared_bf = secrets.token_bytes(32).hex().upper()

        sender_c1, sender_c2, _ = encryption.encrypt(None, sender_pub, amount_to_send, shared_bf)
        dest_c1, dest_c2, _ = encryption.encrypt(None, dest_pub, amount_to_send, shared_bf)
        issuer_c1, issuer_c2, _ = encryption.encrypt(None, issuer_pub, amount_to_send, shared_bf)

        # This test verifies that encryption works correctly with the same blinding factor
        # Full send proof generation requires additional utility layer functions
        # that will be tested when those wrappers are implemented

        # For now, verify that all encryptions succeeded
        self.assertEqual(len(sender_c1), 66)
        self.assertEqual(len(dest_c1), 66)
        self.assertEqual(len(issuer_c1), 66)


class TestConfidentialConvertBack(unittest.TestCase):
    """Test confidential convert back transaction (mirrors test_mpt_convert_back)."""

    def test_convert_back_transaction(self):
        """Test generating convert back proof (balance linkage proof)."""
        # Setup mock account, issuance and transaction details
        acc = create_mock_account_id(0x55)
        issuance = create_mock_issuance_id(0xEE)
        seq = 98765
        current_balance = 5000
        amount_to_convert_back = 1000
        version = 2

        # Generate keypair
        privkey, pubkey = keypair.generate_keypair()

        # Mock spending confidential balance (ElGamal ciphertext currently stored on-chain)
        bal_bf = secrets.token_bytes(32).hex().upper()
        bal_c1, bal_c2, _ = encryption.encrypt(None, pubkey, current_balance, bal_bf)

        # Generate context hash
        tx_hash = context.compute_convert_back_context_hash(
            acc,
            seq,
            issuance,
            amount_to_convert_back,
            version
        )

        # Generate Pedersen commitment for current balance
        pcm_bf = secrets.token_bytes(32).hex().upper()
        pcm_comm = commitments.create_pedersen_commitment(None, current_balance, pcm_bf)

        # Generate balance linkage proof
        # Note: Function signature expects c2, c1 (not c1, c2)
        proof = link_proofs.create_balance_link_proof(
            None,
            pubkey,
            bal_c2,
            bal_c1,
            pcm_comm,
            current_balance,
            privkey,
            pcm_bf,
            tx_hash
        )

        # Verify proof length (195 bytes = 390 hex chars)
        self.assertEqual(len(proof), 390)

        # Verify the proof using low-level secp256k1 functions
        ctx = lib.mpt_secp256k1_context()
        self.assertNotEqual(ctx, ffi.NULL)

        # Parse points
        c1_bytes = bytes.fromhex(bal_c1)
        c2_bytes = bytes.fromhex(bal_c2)
        pk_bytes = bytes.fromhex(pubkey)
        pcm_bytes = bytes.fromhex(pcm_comm)
        proof_bytes = bytes.fromhex(proof)
        tx_hash_bytes = bytes.fromhex(tx_hash)

        c1_pk = ffi.new("secp256k1_pubkey *")
        c2_pk = ffi.new("secp256k1_pubkey *")
        pk = ffi.new("secp256k1_pubkey *")
        pcm_pk = ffi.new("secp256k1_pubkey *")

        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, c1_pk, c1_bytes, 33), 1)
        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, c2_pk, c2_bytes, 33), 1)
        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, pk, pk_bytes, 33), 1)
        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, pcm_pk, pcm_bytes, 33), 1)

        # Verify balance linkage proof
        # Note: The order is pk, c2, c1 (not c1, c2, pk) as per the C++ reference
        self.assertEqual(
            lib.secp256k1_elgamal_pedersen_link_verify(
                ctx, proof_bytes, pk, c2_pk, c1_pk, pcm_pk, tx_hash_bytes
            ),
            1
        )


class TestConfidentialClawback(unittest.TestCase):
    """Test confidential clawback transaction (mirrors test_mpt_clawback)."""

    def test_clawback_transaction(self):
        """Test generating clawback proof (equality plaintext proof)."""
        # Setup mock account, issuance and transaction details
        issuer_acc = create_mock_account_id(0x11)
        holder_acc = create_mock_account_id(0x22)
        issuance = create_mock_issuance_id(0xCC)
        seq = 200
        claw_amount = 500

        # Generate issuer keypair
        issuer_priv, issuer_pub = keypair.generate_keypair()

        # Generate context hash
        tx_hash = context.compute_clawback_context_hash(
            issuer_acc,
            seq,
            issuance,
            claw_amount,
            holder_acc
        )

        # Mock holder's "sfIssuerEncryptedBalance"
        bf = secrets.token_bytes(32).hex().upper()
        c1, c2, _ = encryption.encrypt(None, issuer_pub, claw_amount, bf)

        # Generate clawback proof (equality plaintext proof)
        # Note: Pass private key, not blinding factor
        proof = plaintext_proofs.create_equality_plaintext_proof(
            None,
            issuer_pub,
            c2,
            c1,
            claw_amount,
            issuer_priv,
            tx_hash
        )

        # Verify proof length (98 bytes = 196 hex chars)
        self.assertEqual(len(proof), 196)

        # Verify the proof using low-level secp256k1 functions
        ctx = lib.mpt_secp256k1_context()
        self.assertNotEqual(ctx, ffi.NULL)

        # Parse points
        c1_bytes = bytes.fromhex(c1)
        c2_bytes = bytes.fromhex(c2)
        pk_bytes = bytes.fromhex(issuer_pub)
        proof_bytes = bytes.fromhex(proof)
        tx_hash_bytes = bytes.fromhex(tx_hash)

        c1_pk = ffi.new("secp256k1_pubkey *")
        c2_pk = ffi.new("secp256k1_pubkey *")
        pk = ffi.new("secp256k1_pubkey *")

        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, c1_pk, c1_bytes, 33), 1)
        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, c2_pk, c2_bytes, 33), 1)
        self.assertEqual(lib.secp256k1_ec_pubkey_parse(ctx, pk, pk_bytes, 33), 1)

        # Verify equality plaintext proof
        # Note: The order is pk, c2, c1 (not c1, c2, pk) as per the C++ reference
        self.assertEqual(
            lib.secp256k1_equality_plaintext_verify(
                ctx, proof_bytes, pk, c2_pk, c1_pk, claw_amount, tx_hash_bytes
            ),
            1
        )


if __name__ == "__main__":
    unittest.main()


