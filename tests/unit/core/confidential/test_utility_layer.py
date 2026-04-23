"""
Test suite for MPT utility layer functions.

This test suite mirrors the C++ tests in
XRPLF/mpt-crypto/tests/test_mpt_utility.cpp to ensure
the Python wrappers correctly call the utility layer functions.

NOTE: The C utility functions return 0 on success (not 1).
"""

import unittest

from xrpl.core.confidential.crypto_bindings import ffi, lib


# ---------------------------------------------------------------------------
# Helpers (matching the C++ test helpers)
# ---------------------------------------------------------------------------


def create_mock_account_id(fill_byte: int) -> bytes:
    """Create a mock 20-byte account ID filled with a specific byte."""
    return bytes([fill_byte] * 20)


def create_mock_issuance_id(fill_byte: int) -> bytes:
    """Create a mock 24-byte MPT issuance ID."""
    return bytes([fill_byte] * 24)


def make_account_id(fill_byte: int):
    """Create an account_id struct for the C API."""
    acc = ffi.new("account_id *")
    for i in range(20):
        acc.bytes[i] = fill_byte
    return acc[0]


def make_issuance_id(fill_byte: int):
    """Create an mpt_issuance_id struct for the C API."""
    iss = ffi.new("mpt_issuance_id *")
    for i in range(24):
        iss.bytes[i] = fill_byte
    return iss[0]


def generate_keypair():
    """Generate an ElGamal keypair using the C API. Returns (priv, pub) as raw bytes."""
    priv = ffi.new("uint8_t[32]")
    pub = ffi.new("uint8_t[33]")
    assert lib.mpt_generate_keypair(priv, pub) == 0
    return bytes(priv[0:32]), bytes(pub[0:33])


def generate_blinding_factor():
    """Generate a valid blinding factor using the C API. Returns raw bytes."""
    bf = ffi.new("uint8_t[32]")
    assert lib.mpt_generate_blinding_factor(bf) == 0
    return bytes(bf[0:32])


def encrypt_amount(amount, pubkey_bytes, bf_bytes):
    """Encrypt an amount. Returns 66-byte ciphertext as raw bytes."""
    ct = ffi.new("uint8_t[66]")
    assert lib.mpt_encrypt_amount(amount, pubkey_bytes, bf_bytes, ct) == 0
    return bytes(ct[0:66])


def get_pedersen_commitment(amount, bf_bytes):
    """Compute a Pedersen commitment. Returns 33-byte commitment as raw bytes."""
    comm = ffi.new("uint8_t[33]")
    assert lib.mpt_get_pedersen_commitment(amount, bf_bytes, comm) == 0
    return bytes(comm[0:33])


# ---------------------------------------------------------------------------
# SendFixture — mirrors the C++ SendFixture struct + make_send_fixture()
# ---------------------------------------------------------------------------


class SendFixture:
    """Holds all data for a confidential send proof, matching the C++ SendFixture."""

    pass


def make_send_fixture(n_participants=3):
    """Build a fully-initialised send fixture and generate the proof.

    Mirrors the C++ make_send_fixture() helper exactly.
    """
    f = SendFixture()

    amount_to_send = 100
    prev_balance = 2000

    sender_acc = make_account_id(0x11)
    dest_acc = make_account_id(0x22)
    issuance = make_issuance_id(0xBB)
    seq = 54321
    version = 1

    # Keypairs — only the sender's private key is needed by the prover
    f.sender_priv, f.sender_pub = generate_keypair()
    _, f.dest_pub = generate_keypair()
    _, f.issuer_pub = generate_keypair()
    _, f.auditor_pub = generate_keypair()

    # Shared ciphertext randomness r — also used as PC_m blinding factor (spec §3.3)
    f.shared_bf = generate_blinding_factor()
    f.sender_ct = encrypt_amount(amount_to_send, f.sender_pub, f.shared_bf)
    f.dest_ct = encrypt_amount(amount_to_send, f.dest_pub, f.shared_bf)
    f.issuer_ct = encrypt_amount(amount_to_send, f.issuer_pub, f.shared_bf)
    f.auditor_ct = encrypt_amount(amount_to_send, f.auditor_pub, f.shared_bf)

    # PC_m = m*G + r*H  (r == shared_bf, per spec §3.3)
    f.amount_comm = get_pedersen_commitment(amount_to_send, f.shared_bf)

    # PC_b = b*G + rho*H  (independent blinding factor)
    f.balance_bf = generate_blinding_factor()
    f.balance_comm = get_pedersen_commitment(prev_balance, f.balance_bf)

    # Sender's on-ledger spending-balance ciphertext (B1||B2)
    bal_bf = generate_blinding_factor()
    f.bal_ct = encrypt_amount(prev_balance, f.sender_pub, bal_bf)

    # Context hash
    f.ctx_hash = ffi.new("uint8_t[32]")
    assert (
        lib.mpt_get_send_context_hash(
            sender_acc, issuance, seq, dest_acc, version, f.ctx_hash
        )
        == 0
    )
    f.ctx_hash = bytes(f.ctx_hash[0:32])

    # Balance params
    f.bal_params = ffi.new("mpt_pedersen_proof_params *")
    f.bal_params.amount = prev_balance
    ffi.memmove(f.bal_params.blinding_factor, f.balance_bf, 32)
    ffi.memmove(f.bal_params.pedersen_commitment, f.balance_comm, 33)
    ffi.memmove(f.bal_params.ciphertext, f.bal_ct, 66)

    # Build participant list
    participants = ffi.new(f"mpt_confidential_participant[{n_participants}]")
    for i, (pub, ct) in enumerate(
        [(f.sender_pub, f.sender_ct), (f.dest_pub, f.dest_ct), (f.issuer_pub, f.issuer_ct)]
    ):
        ffi.memmove(participants[i].pubkey, pub, 33)
        ffi.memmove(participants[i].ciphertext, ct, 66)
    if n_participants == 4:
        ffi.memmove(participants[3].pubkey, f.auditor_pub, 33)
        ffi.memmove(participants[3].ciphertext, f.auditor_ct, 66)

    f.participants = participants
    f.n_participants = n_participants

    # Generate proof
    proof_size = lib.SECP256K1_COMPACT_STANDARD_PROOF_SIZE + lib.kMPT_DOUBLE_BULLETPROOF_SIZE
    f.proof = ffi.new(f"uint8_t[{proof_size}]")
    out_len = ffi.new("size_t *", proof_size)

    assert (
        lib.mpt_get_confidential_send_proof(
            f.sender_priv,
            f.sender_pub,
            amount_to_send,
            participants,
            n_participants,
            f.shared_bf,
            f.ctx_hash,
            f.amount_comm,
            f.bal_params,
            f.proof,
            out_len,
        )
        == 0
    )

    f.proof_len = out_len[0]
    f.proof_bytes = bytes(ffi.buffer(f.proof, f.proof_len))

    return f


# ===========================================================================
# Integration Tests
# ===========================================================================


class TestEncryptionDecryptionIntegrate(unittest.TestCase):
    """Mirrors test_encryption_decryption_integrate."""

    def test_encrypt_decrypt_roundtrip(self):
        priv, pub = generate_keypair()

        # todo: due to the lib's current limitation, large numbers
        # are not supported yet.
        test_amounts = [0, 1, 1000]

        for original_amount in test_amounts:
            with self.subTest(amount=original_amount):
                bf = generate_blinding_factor()
                ct = encrypt_amount(original_amount, pub, bf)

                decrypted = ffi.new("uint64_t *")
                self.assertEqual(lib.mpt_decrypt_amount(ct, priv, decrypted), 0)
                self.assertEqual(decrypted[0], original_amount)


class TestConfidentialConvertIntegrate(unittest.TestCase):
    """Mirrors test_mpt_confidential_convert_integrate."""

    def test_convert_prove_and_verify(self):
        acc = make_account_id(0xAA)
        issuance = make_issuance_id(0xBB)
        seq = 12345
        convert_amount = 750

        priv, pub = generate_keypair()
        bf = generate_blinding_factor()
        encrypt_amount(convert_amount, pub, bf)

        # Context hash
        tx_hash = ffi.new("uint8_t[32]")
        self.assertEqual(lib.mpt_get_convert_context_hash(acc, issuance, seq, tx_hash), 0)

        # Prove
        proof = ffi.new(f"uint8_t[{lib.kMPT_SCHNORR_PROOF_SIZE}]")
        self.assertEqual(lib.mpt_get_convert_proof(pub, priv, tx_hash, proof), 0)

        # Verify
        self.assertEqual(lib.mpt_verify_convert_proof(proof, pub, tx_hash), 0)


class TestConfidentialSendIntegrate(unittest.TestCase):
    """Mirrors test_mpt_confidential_send_integrate."""

    def test_send_prove_and_verify(self):
        sender_acc = make_account_id(0x11)
        dest_acc = make_account_id(0x22)
        issuance = make_issuance_id(0xBB)
        seq = 54321
        amount_to_send = 100
        prev_balance = 2000
        version = 1

        # Keypairs
        sender_priv, sender_pub = generate_keypair()
        _, dest_pub = generate_keypair()
        _, issuer_pub = generate_keypair()

        # Transaction ciphertexts — all encrypted with the same shared r
        shared_bf = generate_blinding_factor()
        sender_ct = encrypt_amount(amount_to_send, sender_pub, shared_bf)
        dest_ct = encrypt_amount(amount_to_send, dest_pub, shared_bf)
        issuer_ct = encrypt_amount(amount_to_send, issuer_pub, shared_bf)

        # Participants list (sender first)
        participants = ffi.new("mpt_confidential_participant[3]")
        for i, (pub, ct) in enumerate(
            [(sender_pub, sender_ct), (dest_pub, dest_ct), (issuer_pub, issuer_ct)]
        ):
            ffi.memmove(participants[i].pubkey, pub, 33)
            ffi.memmove(participants[i].ciphertext, ct, 66)

        amount_comm = get_pedersen_commitment(amount_to_send, shared_bf)

        balance_bf = generate_blinding_factor()
        balance_comm = get_pedersen_commitment(prev_balance, balance_bf)

        prev_bal_bf = generate_blinding_factor()
        prev_bal_ct = encrypt_amount(prev_balance, sender_pub, prev_bal_bf)

        # Context hash
        send_ctx_hash = ffi.new("uint8_t[32]")
        self.assertEqual(
            lib.mpt_get_send_context_hash(
                sender_acc, issuance, seq, dest_acc, version, send_ctx_hash
            ),
            0,
        )

        bal_params = ffi.new("mpt_pedersen_proof_params *")
        bal_params.amount = prev_balance
        ffi.memmove(bal_params.blinding_factor, balance_bf, 32)
        ffi.memmove(bal_params.pedersen_commitment, balance_comm, 33)
        ffi.memmove(bal_params.ciphertext, prev_bal_ct, 66)

        # Generate proof
        proof_size = lib.SECP256K1_COMPACT_STANDARD_PROOF_SIZE + lib.kMPT_DOUBLE_BULLETPROOF_SIZE
        proof = ffi.new(f"uint8_t[{proof_size}]")
        out_len = ffi.new("size_t *", proof_size)

        self.assertEqual(
            lib.mpt_get_confidential_send_proof(
                sender_priv,
                sender_pub,
                amount_to_send,
                participants,
                3,
                shared_bf,
                send_ctx_hash,
                amount_comm,
                bal_params,
                proof,
                out_len,
            ),
            0,
        )

        # Verify
        self.assertEqual(
            lib.mpt_verify_send_proof(
                proof,
                participants,
                3,
                prev_bal_ct,
                amount_comm,
                balance_comm,
                send_ctx_hash,
            ),
            0,
        )


class TestConvertBackIntegrate(unittest.TestCase):
    """Mirrors test_mpt_convert_back_integrate."""

    def test_convert_back_prove_and_verify(self):
        acc = make_account_id(0x55)
        issuance = make_issuance_id(0xEE)
        seq = 98765
        current_balance = 5000
        amount_to_convert_back = 1000
        version = 2

        priv, pub = generate_keypair()

        bal_bf = generate_blinding_factor()
        spending_bal_ct = encrypt_amount(current_balance, pub, bal_bf)

        # Context hash
        context_hash = ffi.new("uint8_t[32]")
        self.assertEqual(
            lib.mpt_get_convert_back_context_hash(acc, issuance, seq, version, context_hash), 0
        )

        pcb_bf = generate_blinding_factor()
        pcb_comm = get_pedersen_commitment(current_balance, pcb_bf)

        # Pedersen proof params
        pc_params = ffi.new("mpt_pedersen_proof_params *")
        pc_params.amount = current_balance
        ffi.memmove(pc_params.blinding_factor, pcb_bf, 32)
        ffi.memmove(pc_params.pedersen_commitment, pcb_comm, 33)
        ffi.memmove(pc_params.ciphertext, spending_bal_ct, 66)

        # Generate proof
        proof_size = lib.SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE + lib.kMPT_SINGLE_BULLETPROOF_SIZE
        proof = ffi.new(f"uint8_t[{proof_size}]")
        self.assertEqual(
            lib.mpt_get_convert_back_proof(priv, pub, context_hash, amount_to_convert_back, pc_params, proof),
            0,
        )

        # Verify
        self.assertEqual(
            lib.mpt_verify_convert_back_proof(
                proof, pub, spending_bal_ct, pcb_comm, amount_to_convert_back, context_hash
            ),
            0,
        )


class TestClawbackIntegrate(unittest.TestCase):
    """Mirrors test_mpt_clawback_integrate."""

    def test_clawback_prove_and_verify(self):
        issuer_acc = make_account_id(0x11)
        holder_acc = make_account_id(0x22)
        issuance = make_issuance_id(0xCC)
        seq = 200
        claw_amount = 500

        issuer_priv, issuer_pub = generate_keypair()

        # Context hash
        context_hash = ffi.new("uint8_t[32]")
        self.assertEqual(
            lib.mpt_get_clawback_context_hash(issuer_acc, issuance, seq, holder_acc, context_hash),
            0,
        )

        bf = generate_blinding_factor()
        issuer_encrypted_bal = encrypt_amount(claw_amount, issuer_pub, bf)

        # Prove
        proof = ffi.new(f"uint8_t[{lib.SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE}]")
        self.assertEqual(
            lib.mpt_get_clawback_proof(
                issuer_priv, issuer_pub, context_hash, claw_amount, issuer_encrypted_bal, proof
            ),
            0,
        )

        # Verify
        self.assertEqual(
            lib.mpt_verify_clawback_proof(
                proof, claw_amount, issuer_pub, issuer_encrypted_bal, context_hash
            ),
            0,
        )


# ===========================================================================
# Unit Tests
# ===========================================================================


class TestConfidentialConvert(unittest.TestCase):
    """Mirrors test_mpt_confidential_convert (unit tests with rejection paths)."""

    def test_valid_prove_and_verify(self):
        acc = make_account_id(0xAA)
        issuance = make_issuance_id(0xBB)
        seq = 12345

        priv, pub = generate_keypair()
        tx_hash = ffi.new("uint8_t[32]")
        self.assertEqual(lib.mpt_get_convert_context_hash(acc, issuance, seq, tx_hash), 0)

        proof = ffi.new(f"uint8_t[{lib.kMPT_SCHNORR_PROOF_SIZE}]")
        self.assertEqual(lib.mpt_get_convert_proof(pub, priv, tx_hash, proof), 0)
        self.assertEqual(lib.mpt_verify_convert_proof(proof, pub, tx_hash), 0)

    def test_invalid_corrupted_proof_byte(self):
        acc = make_account_id(0xAA)
        issuance = make_issuance_id(0xBB)

        priv, pub = generate_keypair()
        tx_hash = ffi.new("uint8_t[32]")
        self.assertEqual(lib.mpt_get_convert_context_hash(acc, issuance, 1, tx_hash), 0)

        proof = ffi.new(f"uint8_t[{lib.kMPT_SCHNORR_PROOF_SIZE}]")
        self.assertEqual(lib.mpt_get_convert_proof(pub, priv, tx_hash, proof), 0)

        # Corrupt first byte
        proof[0] ^= 0xFF
        self.assertNotEqual(lib.mpt_verify_convert_proof(proof, pub, tx_hash), 0)

    def test_invalid_wrong_context_hash(self):
        acc = make_account_id(0xAA)
        issuance = make_issuance_id(0xBB)

        priv, pub = generate_keypair()
        tx_hash = ffi.new("uint8_t[32]")
        self.assertEqual(lib.mpt_get_convert_context_hash(acc, issuance, 1, tx_hash), 0)

        proof = ffi.new(f"uint8_t[{lib.kMPT_SCHNORR_PROOF_SIZE}]")
        self.assertEqual(lib.mpt_get_convert_proof(pub, priv, tx_hash, proof), 0)

        bad_hash = b"\x00" * 32
        self.assertNotEqual(lib.mpt_verify_convert_proof(proof, pub, bad_hash), 0)

    def test_invalid_wrong_public_key(self):
        acc = make_account_id(0xAA)
        issuance = make_issuance_id(0xBB)

        priv, pub = generate_keypair()
        tx_hash = ffi.new("uint8_t[32]")
        self.assertEqual(lib.mpt_get_convert_context_hash(acc, issuance, 1, tx_hash), 0)

        proof = ffi.new(f"uint8_t[{lib.kMPT_SCHNORR_PROOF_SIZE}]")
        self.assertEqual(lib.mpt_get_convert_proof(pub, priv, tx_hash, proof), 0)

        _, other_pub = generate_keypair()
        self.assertNotEqual(lib.mpt_verify_convert_proof(proof, other_pub, tx_hash), 0)


class TestConfidentialSend(unittest.TestCase):
    """Mirrors test_mpt_confidential_send (unit tests with rejection paths)."""

    def test_valid_n3(self):
        """valid: n=3 (sender, dest, issuer)"""
        f = make_send_fixture(3)

        # Proof size must be exactly 192 (compact sigma) + 754 (bulletproof)
        expected = lib.SECP256K1_COMPACT_STANDARD_PROOF_SIZE + lib.kMPT_DOUBLE_BULLETPROOF_SIZE
        self.assertEqual(f.proof_len, expected)

        self.assertEqual(
            lib.mpt_verify_send_proof(
                f.proof, f.participants, f.n_participants,
                f.bal_ct, f.amount_comm, f.balance_comm, f.ctx_hash,
            ),
            0,
        )

    def test_valid_n4(self):
        """valid: n=4 (sender, dest, issuer, auditor)"""
        f = make_send_fixture(4)

        expected = lib.SECP256K1_COMPACT_STANDARD_PROOF_SIZE + lib.kMPT_DOUBLE_BULLETPROOF_SIZE
        self.assertEqual(f.proof_len, expected)

        self.assertEqual(
            lib.mpt_verify_send_proof(
                f.proof, f.participants, f.n_participants,
                f.bal_ct, f.amount_comm, f.balance_comm, f.ctx_hash,
            ),
            0,
        )

    def test_invalid_corrupted_proof_byte(self):
        f = make_send_fixture(3)

        # Corrupt first byte
        proof_copy = bytearray(f.proof_bytes)
        proof_copy[0] ^= 0xFF

        self.assertNotEqual(
            lib.mpt_verify_send_proof(
                bytes(proof_copy), f.participants, f.n_participants,
                f.bal_ct, f.amount_comm, f.balance_comm, f.ctx_hash,
            ),
            0,
        )

    def test_invalid_wrong_context_hash(self):
        f = make_send_fixture(3)
        bad_ctx = b"\x00" * 32

        self.assertNotEqual(
            lib.mpt_verify_send_proof(
                f.proof, f.participants, f.n_participants,
                f.bal_ct, f.amount_comm, f.balance_comm, bad_ctx,
            ),
            0,
        )

    def test_invalid_wrong_amount_commitment(self):
        """PC_m mismatch"""
        f = make_send_fixture(3)

        bad_bf = generate_blinding_factor()
        bad_amt_comm = get_pedersen_commitment(100, bad_bf)  # same amount, different blinding

        self.assertNotEqual(
            lib.mpt_verify_send_proof(
                f.proof, f.participants, f.n_participants,
                f.bal_ct, bad_amt_comm, f.balance_comm, f.ctx_hash,
            ),
            0,
        )

    def test_invalid_wrong_balance_ciphertext(self):
        """B1/B2 mismatch"""
        f = make_send_fixture(3)

        bad_bf = generate_blinding_factor()
        bad_bal_ct = encrypt_amount(2000, f.sender_pub, bad_bf)

        self.assertNotEqual(
            lib.mpt_verify_send_proof(
                f.proof, f.participants, f.n_participants,
                bad_bal_ct, f.amount_comm, f.balance_comm, f.ctx_hash,
            ),
            0,
        )

    def test_invalid_wrong_balance_commitment(self):
        """PC_b mismatch"""
        f = make_send_fixture(3)

        bad_bf = generate_blinding_factor()
        bad_bal_comm = get_pedersen_commitment(2000, bad_bf)

        self.assertNotEqual(
            lib.mpt_verify_send_proof(
                f.proof, f.participants, f.n_participants,
                f.bal_ct, f.amount_comm, bad_bal_comm, f.ctx_hash,
            ),
            0,
        )


class TestConvertBack(unittest.TestCase):
    """Mirrors test_mpt_convert_back (unit tests with rejection paths)."""

    def _make_convert_back_fixture(self):
        """Helper to build a valid convert back proof (reused across sub-tests)."""
        acc = make_account_id(0x55)
        issuance = make_issuance_id(0xEE)
        seq = 98765
        current_balance = 5000
        amount_to_convert_back = 1000
        version = 2

        priv, pub = generate_keypair()

        bal_bf = generate_blinding_factor()
        spending_bal_ct = encrypt_amount(current_balance, pub, bal_bf)

        ctx = ffi.new("uint8_t[32]")
        assert lib.mpt_get_convert_back_context_hash(acc, issuance, seq, version, ctx) == 0
        ctx_bytes = bytes(ctx[0:32])

        pcb_bf = generate_blinding_factor()
        pcb_comm = get_pedersen_commitment(current_balance, pcb_bf)

        pc_params = ffi.new("mpt_pedersen_proof_params *")
        pc_params.amount = current_balance
        ffi.memmove(pc_params.blinding_factor, pcb_bf, 32)
        ffi.memmove(pc_params.pedersen_commitment, pcb_comm, 33)
        ffi.memmove(pc_params.ciphertext, spending_bal_ct, 66)

        proof_size = lib.SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE + lib.kMPT_SINGLE_BULLETPROOF_SIZE
        proof = ffi.new(f"uint8_t[{proof_size}]")
        assert (
            lib.mpt_get_convert_back_proof(priv, pub, ctx_bytes, amount_to_convert_back, pc_params, proof)
            == 0
        )

        return {
            "proof": proof,
            "proof_bytes": bytes(ffi.buffer(proof, proof_size)),
            "pub": pub,
            "spending_bal_ct": spending_bal_ct,
            "pcb_comm": pcb_comm,
            "amount": amount_to_convert_back,
            "ctx": ctx_bytes,
        }

    def test_valid_prove_and_verify(self):
        fx = self._make_convert_back_fixture()
        self.assertEqual(
            lib.mpt_verify_convert_back_proof(
                fx["proof"], fx["pub"], fx["spending_bal_ct"],
                fx["pcb_comm"], fx["amount"], fx["ctx"],
            ),
            0,
        )

    def test_invalid_corrupted_proof_byte(self):
        fx = self._make_convert_back_fixture()

        bad_proof = bytearray(fx["proof_bytes"])
        bad_proof[0] ^= 0xFF

        self.assertNotEqual(
            lib.mpt_verify_convert_back_proof(
                bytes(bad_proof), fx["pub"], fx["spending_bal_ct"],
                fx["pcb_comm"], fx["amount"], fx["ctx"],
            ),
            0,
        )

    def test_invalid_wrong_context_hash(self):
        fx = self._make_convert_back_fixture()
        bad_ctx = b"\x00" * 32

        self.assertNotEqual(
            lib.mpt_verify_convert_back_proof(
                fx["proof"], fx["pub"], fx["spending_bal_ct"],
                fx["pcb_comm"], fx["amount"], bad_ctx,
            ),
            0,
        )

    def test_invalid_wrong_balance_commitment(self):
        """PC_b mismatch"""
        fx = self._make_convert_back_fixture()

        bad_bf = generate_blinding_factor()
        bad_comm = get_pedersen_commitment(5000, bad_bf)

        self.assertNotEqual(
            lib.mpt_verify_convert_back_proof(
                fx["proof"], fx["pub"], fx["spending_bal_ct"],
                bad_comm, fx["amount"], fx["ctx"],
            ),
            0,
        )

    def test_invalid_wrong_balance_ciphertext(self):
        """B1/B2 mismatch"""
        fx = self._make_convert_back_fixture()

        bad_bf = generate_blinding_factor()
        bad_ct = encrypt_amount(5000, fx["pub"], bad_bf)

        self.assertNotEqual(
            lib.mpt_verify_convert_back_proof(
                fx["proof"], fx["pub"], bad_ct,
                fx["pcb_comm"], fx["amount"], fx["ctx"],
            ),
            0,
        )


class TestClawback(unittest.TestCase):
    """Mirrors test_mpt_clawback (unit tests with rejection paths)."""

    def _make_clawback_fixture(self):
        """Helper to build a valid clawback proof (reused across sub-tests)."""
        issuer_acc = make_account_id(0x11)
        holder_acc = make_account_id(0x22)
        issuance = make_issuance_id(0xCC)
        seq = 200
        claw_amount = 500

        issuer_priv, issuer_pub = generate_keypair()

        ctx = ffi.new("uint8_t[32]")
        assert (
            lib.mpt_get_clawback_context_hash(issuer_acc, issuance, seq, holder_acc, ctx) == 0
        )
        ctx_bytes = bytes(ctx[0:32])

        bf = generate_blinding_factor()
        ct = encrypt_amount(claw_amount, issuer_pub, bf)

        proof = ffi.new(f"uint8_t[{lib.SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE}]")
        assert (
            lib.mpt_get_clawback_proof(issuer_priv, issuer_pub, ctx_bytes, claw_amount, ct, proof)
            == 0
        )

        return {
            "proof": proof,
            "proof_bytes": bytes(ffi.buffer(proof, lib.SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE)),
            "amount": claw_amount,
            "issuer_pub": issuer_pub,
            "ct": ct,
            "ctx": ctx_bytes,
        }

    def test_valid_prove_and_verify(self):
        fx = self._make_clawback_fixture()
        self.assertEqual(
            lib.mpt_verify_clawback_proof(
                fx["proof"], fx["amount"], fx["issuer_pub"], fx["ct"], fx["ctx"]
            ),
            0,
        )

    def test_invalid_corrupted_proof_byte(self):
        fx = self._make_clawback_fixture()

        bad_proof = bytearray(fx["proof_bytes"])
        bad_proof[0] ^= 0xFF

        self.assertNotEqual(
            lib.mpt_verify_clawback_proof(
                bytes(bad_proof), fx["amount"], fx["issuer_pub"], fx["ct"], fx["ctx"]
            ),
            0,
        )

    def test_invalid_wrong_context_hash(self):
        fx = self._make_clawback_fixture()
        bad_ctx = b"\x00" * 32

        self.assertNotEqual(
            lib.mpt_verify_clawback_proof(
                fx["proof"], fx["amount"], fx["issuer_pub"], fx["ct"], bad_ctx
            ),
            0,
        )

    def test_invalid_wrong_amount(self):
        fx = self._make_clawback_fixture()

        self.assertNotEqual(
            lib.mpt_verify_clawback_proof(
                fx["proof"], 999, fx["issuer_pub"], fx["ct"], fx["ctx"]
            ),
            0,
        )

    def test_invalid_wrong_ciphertext(self):
        """C1/C2 mismatch"""
        fx = self._make_clawback_fixture()

        bad_bf = generate_blinding_factor()
        bad_ct = encrypt_amount(500, fx["issuer_pub"], bad_bf)

        self.assertNotEqual(
            lib.mpt_verify_clawback_proof(
                fx["proof"], fx["amount"], fx["issuer_pub"], bad_ct, fx["ctx"]
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
