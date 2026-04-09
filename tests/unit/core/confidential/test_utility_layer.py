"""
Test suite for MPT utility layer functions.

This test suite mirrors the C++ tests in
tools/mpt-crypto-main/tests/test_mpt_utility.cpp to ensure
the Python wrappers correctly call the utility layer functions.

NOTE: The C utility functions return 0 on success (not 1).
"""

import secrets
import unittest

from xrpl.core.confidential import commitments, context, encryption, keypair
from xrpl.core.confidential.crypto_bindings import ffi, lib


def create_mock_account_id(fill_byte: int) -> str:
    """Create a mock 20-byte account ID filled with a specific byte as hex string."""
    return bytes([fill_byte] * 20).hex().upper()


def create_mock_issuance_id(fill_byte: int) -> str:
    """Create a mock 24-byte MPT issuance ID as hex string."""
    return bytes([fill_byte] * 24).hex().upper()


class TestEncryptionDecryption(unittest.TestCase):
    """Test encryption and decryption using utility layer."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption/decryption for various amounts."""
        privkey, pubkey = keypair.generate_keypair()

        # Large numbers not supported yet due to discrete log limitation
        test_amounts = [0, 1, 1000]

        for amount in test_amounts:
            with self.subTest(amount=amount):
                blinding_factor = secrets.token_bytes(32).hex().upper()

                c1, c2, returned_bf = encryption.encrypt(
                    None, pubkey, amount, blinding_factor
                )

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

        # Generate keypair, blinding factor and encrypt the amount
        privkey, pubkey = keypair.generate_keypair()
        bf = secrets.token_bytes(32).hex().upper()
        encryption.encrypt(None, pubkey, convert_amount, bf)

        # Generate context hash and ZKProof
        tx_hash = context.compute_convert_context_hash(acc, seq, issuance)
        proof = keypair.generate_pok(None, privkey, pubkey, tx_hash)

        # Verify proof length (64 bytes = 128 hex chars)
        self.assertEqual(len(proof), 128)

        # Verify the ZKProof for convert
        self.assertEqual(
            lib.mpt_verify_convert_proof(
                bytes.fromhex(proof), bytes.fromhex(pubkey), bytes.fromhex(tx_hash)
            ),
            0,
        )


class TestConfidentialSend(unittest.TestCase):
    """Test confidential send transaction (mirrors test_mpt_confidential_send)."""

    def test_send_transaction(self):
        """Test generating confidential send proof with bulletproof."""
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

        # Encrypt for all participants (using same shared blinding factor)
        shared_bf = secrets.token_bytes(32).hex().upper()

        sender_c1, sender_c2, _ = encryption.encrypt(
            None, sender_pub, amount_to_send, shared_bf
        )
        dest_c1, dest_c2, _ = encryption.encrypt(
            None, dest_pub, amount_to_send, shared_bf
        )
        issuer_c1, issuer_c2, _ = encryption.encrypt(
            None, issuer_pub, amount_to_send, shared_bf
        )

        sender_ct = sender_c1 + sender_c2
        dest_ct = dest_c1 + dest_c2
        issuer_ct = issuer_c1 + issuer_c2

        # Generate pedersen commitments for amount and balance
        amount_bf = secrets.token_bytes(32).hex().upper()
        amount_comm = commitments.create_pedersen_commitment(
            None, amount_to_send, amount_bf
        )

        balance_bf = secrets.token_bytes(32).hex().upper()
        balance_comm = commitments.create_pedersen_commitment(
            None, prev_balance, balance_bf
        )

        # Generate context hash for the transaction
        tx_hash = context.compute_send_context_hash(
            sender_acc, seq, issuance, dest_acc, version
        )

        # Generate previous balance ciphertext
        prev_bal_bf = secrets.token_bytes(32).hex().upper()
        prev_bal_c1, prev_bal_c2, _ = encryption.encrypt(
            None, sender_pub, prev_balance, prev_bal_bf
        )
        prev_bal_ct = prev_bal_c1 + prev_bal_c2

        # Generate the confidential send proof
        from xrpl.core.confidential.main import MPTCrypto

        crypto = MPTCrypto()

        complete_proof = crypto.create_confidential_send_proof(
            sender_privkey=sender_priv,
            amount=amount_to_send,
            sender_current_balance=prev_balance,
            recipients=[
                (sender_pub, sender_ct),
                (dest_pub, dest_ct),
                (issuer_pub, issuer_ct),
            ],
            tx_blinding_factor=shared_bf,
            context_hash=tx_hash,
            amount_commitment=amount_comm,
            amount_blinding=amount_bf,
            sender_encrypted_amount=sender_ct,
            balance_commitment=balance_comm,
            balance_blinding=balance_bf,
            sender_balance_encrypted=prev_bal_ct,
        )

        # Verify proof size matches library expectation
        expected_size = lib.get_confidential_send_proof_size(3)
        self.assertEqual(len(complete_proof), expected_size * 2)

        # Build participants array for verification
        participants = ffi.new("mpt_confidential_participant[3]")
        for i, (pub, ct) in enumerate(
            [
                (sender_pub, sender_ct),
                (dest_pub, dest_ct),
                (issuer_pub, issuer_ct),
            ]
        ):
            ffi.memmove(participants[i].pubkey, bytes.fromhex(pub), 33)
            ffi.memmove(participants[i].ciphertext, bytes.fromhex(ct), 66)

        # Verify the confidential send proof
        self.assertEqual(
            lib.mpt_verify_send_proof(
                bytes.fromhex(complete_proof),
                expected_size,
                participants,
                3,
                bytes.fromhex(prev_bal_ct),
                bytes.fromhex(amount_comm),
                bytes.fromhex(balance_comm),
                bytes.fromhex(tx_hash),
            ),
            0,
        )


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

        privkey, pubkey = keypair.generate_keypair()

        # Mock spending confidential balance (ElGamal ciphertext on-chain)
        bal_bf = secrets.token_bytes(32).hex().upper()
        bal_c1, bal_c2, _ = encryption.encrypt(None, pubkey, current_balance, bal_bf)
        spending_bal_ct = bal_c1 + bal_c2

        # Generate context hash
        tx_hash = context.compute_convert_back_context_hash(acc, seq, issuance, version)

        # Generate pedersen commitment for current balance
        pcm_bf = secrets.token_bytes(32).hex().upper()
        pcm_comm = commitments.create_pedersen_commitment(None, current_balance, pcm_bf)

        # Generate convert back proof
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

        # Verify the ZKProof for convert back
        self.assertEqual(
            lib.mpt_verify_convert_back_proof(
                bytes.fromhex(complete_proof),
                bytes.fromhex(pubkey),
                bytes.fromhex(spending_bal_ct),
                bytes.fromhex(pcm_comm),
                amount_to_convert_back,
                bytes.fromhex(tx_hash),
            ),
            0,
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
            issuer_acc, seq, issuance, holder_acc
        )

        # Mock holder's "sfIssuerEncryptedBalance"
        bf = secrets.token_bytes(32).hex().upper()
        c1, c2, _ = encryption.encrypt(None, issuer_pub, claw_amount, bf)
        issuer_encrypted_bal = c1 + c2

        # Generate clawback proof using utility layer
        clawback_proof = ffi.new("uint8_t[98]")
        self.assertEqual(
            lib.mpt_get_clawback_proof(
                bytes.fromhex(issuer_priv),
                bytes.fromhex(issuer_pub),
                bytes.fromhex(tx_hash),
                claw_amount,
                bytes.fromhex(issuer_encrypted_bal),
                clawback_proof,
            ),
            0,
        )

        # Verify the clawback proof
        self.assertEqual(
            lib.mpt_verify_clawback_proof(
                clawback_proof,
                claw_amount,
                bytes.fromhex(issuer_pub),
                bytes.fromhex(issuer_encrypted_bal),
                bytes.fromhex(tx_hash),
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
