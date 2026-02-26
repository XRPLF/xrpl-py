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
        """Test generating confidential send proof with bulletproof (using utility layer)."""
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
        _, dest_pub = keypair.generate_keypair()
        _, issuer_pub = keypair.generate_keypair()

        # Encrypt for all recipients using same shared blinding factor
        shared_bf = secrets.token_bytes(32).hex().upper()

        sender_c1, sender_c2, _ = encryption.encrypt(None, sender_pub, amount_to_send, shared_bf)
        dest_c1, dest_c2, _ = encryption.encrypt(None, dest_pub, amount_to_send, shared_bf)
        issuer_c1, issuer_c2, _ = encryption.encrypt(None, issuer_pub, amount_to_send, shared_bf)

        # Generate Pedersen commitments for amount and balance
        amount_bf = secrets.token_bytes(32).hex().upper()
        amount_comm = commitments.create_pedersen_commitment(None, amount_to_send, amount_bf)

        balance_bf = secrets.token_bytes(32).hex().upper()
        balance_comm = commitments.create_pedersen_commitment(None, prev_balance, balance_bf)

        # Generate context hash
        tx_hash = context.compute_send_context_hash(
            sender_acc,
            seq,
            issuance,
            dest_acc,
            version
        )

        # Encrypt previous balance for sender
        prev_bal_bf = secrets.token_bytes(32).hex().upper()
        prev_bal_c1, prev_bal_c2, _ = encryption.encrypt(None, sender_pub, prev_balance, prev_bal_bf)
        prev_bal_ct = prev_bal_c1 + prev_bal_c2

        # Generate complete proof using utility layer
        from xrpl.core.confidential.main import MPTCrypto
        crypto = MPTCrypto()

        complete_proof = crypto.create_confidential_send_proof(
            sender_privkey=sender_priv,
            amount=amount_to_send,
            sender_current_balance=prev_balance,
            recipients=[
                (sender_pub, sender_c1 + sender_c2),
                (dest_pub, dest_c1 + dest_c2),
                (issuer_pub, issuer_c1 + issuer_c2),
            ],
            tx_blinding_factor=shared_bf,
            context_hash=tx_hash,
            amount_commitment=amount_comm,
            amount_blinding=amount_bf,
            sender_encrypted_amount=sender_c1 + sender_c2,
            balance_commitment=balance_comm,
            balance_blinding=balance_bf,
            sender_balance_encrypted=prev_bal_ct,
        )

        # Verify proof length (1503 bytes = 3006 hex chars)
        # 359 (equality) + 195 (amount link) + 195 (balance link) + 754 (bulletproof)
        self.assertEqual(len(complete_proof), 3006)

        # The proof structure is verified by the utility layer itself
        # Here we just verify that the proof was generated successfully


class TestConfidentialConvertBack(unittest.TestCase):
    """Test confidential convert back transaction (mirrors test_mpt_convert_back)."""

    def test_convert_back_transaction(self):
        """Test generating convert back proof with bulletproof (using utility layer)."""
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
        spending_bal_ct = bal_c1 + bal_c2

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

        # Generate complete proof using utility layer (includes linkage proof + bulletproof)
        from xrpl.core.confidential.main import MPTCrypto
        crypto = MPTCrypto()

        complete_proof = crypto.create_confidential_convert_back_proof(
            holder_privkey=privkey,
            holder_pubkey=pubkey,
            amount=amount_to_convert_back,
            current_balance=current_balance,
            context_hash=tx_hash,
            balance_commitment=pcm_comm,
            balance_blinding=pcm_bf,
            holder_balance_encrypted=spending_bal_ct,
        )

        # Verify proof length (883 bytes = 1766 hex chars: 195 + 688)
        self.assertEqual(len(complete_proof), 1766)

        # Verify the linkage proof portion using low-level secp256k1 functions
        ctx = lib.mpt_secp256k1_context()
        self.assertNotEqual(ctx, ffi.NULL)

        # Parse points
        c1_bytes = bytes.fromhex(bal_c1)
        c2_bytes = bytes.fromhex(bal_c2)
        pk_bytes = bytes.fromhex(pubkey)
        pcm_bytes = bytes.fromhex(pcm_comm)
        linkage_proof_bytes = bytes.fromhex(complete_proof[:390])  # First 195 bytes
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
                ctx, linkage_proof_bytes, pk, c2_pk, c1_pk, pcm_pk, tx_hash_bytes
            ),
            1
        )

        # Note: Bulletproof verification requires secp256k1_ec_pubkey_create,
        # secp256k1_ec_pubkey_negate, and secp256k1_ec_pubkey_combine which are
        # not exposed in the Python bindings. The bulletproof is verified by
        # rippled during transaction processing.


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
