"""
Main MPTCrypto class for confidential MPT operations.

This module provides the high-level Python API for mpt-crypto operations
by wrapping the functional modules into a single class interface.
"""

from typing import Optional, Tuple

from typing_extensions import Self

from xrpl.ext.confidential import commitments, encryption, keypair
from xrpl.ext.confidential.crypto_bindings import ffi, lib
from xrpl.ext.confidential.encryption import (
    BLINDING_FACTOR_SIZE,
    PUBKEY_COMPRESSED_SIZE,
)

# Re-export size constants
from xrpl.ext.confidential.keypair import (
    CONTEXT_ID_SIZE,
    PRIVKEY_SIZE,
    SCHNORR_PROOF_SIZE,
)

ACCOUNT_ID_SIZE = 20
MPT_ISSUANCE_ID_SIZE = 24


def _hex_to_fixed_bytes(value: str, expected_len: int, field: str) -> bytes:
    """
    Decode ``value`` from hex and require exactly ``expected_len`` bytes.

    The result is copied into a fixed-size C struct field via ``ffi.memmove``,
    which reads ``expected_len`` bytes from the source regardless of its actual
    length. Validating the decoded length first turns a short or malformed hex
    string into a clear ``ValueError`` instead of an out-of-bounds read.

    Args:
        value: Hex-encoded input string.
        expected_len: Required decoded length, in bytes.
        field: Field name, used in the error message.

    Returns:
        The decoded bytes, guaranteed to be exactly ``expected_len`` long.

    Raises:
        ValueError: If ``value`` does not decode to exactly ``expected_len`` bytes.
    """
    decoded = bytes.fromhex(value)
    if len(decoded) != expected_len:
        raise ValueError(f"{field} must be {expected_len} bytes, got {len(decoded)}")
    return decoded


# Export size constants
__all__ = [
    "MPTCrypto",
    "PRIVKEY_SIZE",
    "PUBKEY_COMPRESSED_SIZE",
    "SCHNORR_PROOF_SIZE",
    "BLINDING_FACTOR_SIZE",
    "CONTEXT_ID_SIZE",
    "ACCOUNT_ID_SIZE",
    "MPT_ISSUANCE_ID_SIZE",
]


class MPTCrypto:
    """High-level Python API for mpt-crypto operations."""

    def __init__(self: Self) -> None:
        """Initialize with mpt-crypto's globally shared secp256k1 context."""
        # Use the context owned by mpt-crypto rather than creating our own:
        # secp256k1_context_create/destroy are not exported by the Windows DLL
        # (secp256k1 is statically linked in). This shared context is what every
        # functional module already uses internally, so nothing else changes.
        # It is owned by the library — do NOT destroy it (hence no __del__).
        self.ctx = lib.mpt_secp256k1_context()
        if self.ctx == ffi.NULL:
            raise RuntimeError("Failed to obtain mpt-crypto secp256k1 context")

    # Keypair generation and Schnorr PoK
    def generate_keypair(self: Self) -> Tuple[str, str]:
        """Generate an ElGamal keypair."""
        return keypair.generate_keypair()

    def generate_keypair_with_pok(
        self: Self, context_id: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """Generate an ElGamal keypair with a Schnorr proof of knowledge."""
        return keypair.generate_keypair_with_pok(context_id)

    def generate_pok(
        self: Self, privkey: str, pubkey_uncompressed: str, context_id: str
    ) -> str:
        """Generate a Schnorr proof of knowledge of the secret key."""
        return keypair.generate_pok(privkey, pubkey_uncompressed, context_id)

    def verify_pok(
        self: Self, pubkey_uncompressed: str, proof: str, context_id: str
    ) -> bool:
        """Verify a Schnorr proof of knowledge of secret key."""
        return keypair.verify_pok(pubkey_uncompressed, proof, context_id)

    # Encryption/Decryption
    def encrypt(
        self: Self,
        pubkey_uncompressed: str,
        amount: int,
        blinding_factor: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        """Encrypt an amount using ElGamal encryption."""
        return encryption.encrypt(pubkey_uncompressed, amount, blinding_factor)

    def decrypt(
        self: Self,
        privkey: str,
        c1: str,
        c2: str,
        range_low: int = 0,
        range_high: int = encryption.DEFAULT_DECRYPT_RANGE_HIGH,
    ) -> int:
        """Decrypt an ElGamal ciphertext.

        Searches for the amount by discrete log over ``[range_low, range_high]``;
        cost scales with the width of the range.
        """
        return encryption.decrypt(privkey, c1, c2, range_low, range_high)

    # Commitments and Bulletproofs
    def create_pedersen_commitment(
        self: Self, amount: int, blinding_factor: str
    ) -> str:
        """Create a Pedersen commitment: PC = amount*G + blinding_factor*H"""
        return commitments.create_pedersen_commitment(amount, blinding_factor)

    def create_bulletproof(
        self: Self, amount: int, blinding_factor: str, pk_base_uncompressed: str
    ) -> str:
        """Create a Bulletproof range proof (Linux/macOS only; see commitments)."""
        return commitments.create_bulletproof(
            amount, blinding_factor, pk_base_uncompressed
        )

    def verify_bulletproof(
        self: Self, proof: str, commitment: str, pk_base_uncompressed: str
    ) -> bool:
        """Verify a Bulletproof range proof (Linux/macOS only; see commitments)."""
        return commitments.verify_bulletproof(proof, commitment, pk_base_uncompressed)

    # Verify proofs using utility layer
    def verify_clawback_proof(
        self: Self,
        proof: str,
        amount: int,
        pubkey_compressed: str,
        ciphertext: str,
        context_hash: str,
    ) -> bool:
        """
        Verify a ConfidentialMPTClawback proof using the utility layer.

        Args:
            proof: Hex string of the compact sigma proof
            amount: The publicly known amount to be clawed back
            pubkey_compressed: 66-char hex string (33-byte issuer's public key)
            ciphertext: 132-char hex string (66-byte IssuerEncryptedBalance)
            context_hash: 64-char hex string (32-byte context hash)

        Returns:
            True if proof is valid, False otherwise
        """
        # Validate every decoded length before the C call: these inputs are
        # untrusted (network/ledger-sourced proofs), and the C function reads
        # fixed sizes regardless of the buffer it is handed.
        proof_bytes = _hex_to_fixed_bytes(proof, 64, "proof")
        pubkey_bytes = _hex_to_fixed_bytes(pubkey_compressed, 33, "pubkey_compressed")
        ciphertext_bytes = _hex_to_fixed_bytes(ciphertext, 66, "ciphertext")
        context_bytes = _hex_to_fixed_bytes(context_hash, 32, "context_hash")

        result = lib.mpt_verify_clawback_proof(
            proof_bytes, amount, pubkey_bytes, ciphertext_bytes, context_bytes
        )
        return result == 0

    def verify_convert_back_proof(
        self: Self,
        proof: str,
        pubkey_compressed: str,
        ciphertext: str,
        balance_commitment: str,
        amount: int,
        context_hash: str,
    ) -> bool:
        """
        Verify a ConfidentialMPTConvertBack proof using the utility layer.

        Args:
            proof: Hex string of the proof (816 bytes)
            pubkey_compressed: 66-char hex string (33-byte holder's public key)
            ciphertext: 132-char hex string (66-byte holder's balance ciphertext)
            balance_commitment: 66-char hex string (33-byte Pedersen commitment)
            amount: The publicly revealed conversion amount
            context_hash: 64-char hex string (32-byte context hash)

        Returns:
            True if proof is valid, False otherwise
        """
        # Validate lengths before the C call (untrusted proof inputs).
        proof_bytes = _hex_to_fixed_bytes(proof, 816, "proof")
        pubkey_bytes = _hex_to_fixed_bytes(pubkey_compressed, 33, "pubkey_compressed")
        ciphertext_bytes = _hex_to_fixed_bytes(ciphertext, 66, "ciphertext")
        commitment_bytes = _hex_to_fixed_bytes(
            balance_commitment, 33, "balance_commitment"
        )
        context_bytes = _hex_to_fixed_bytes(context_hash, 32, "context_hash")

        result = lib.mpt_verify_convert_back_proof(
            proof_bytes,
            pubkey_bytes,
            ciphertext_bytes,
            commitment_bytes,
            amount,
            context_bytes,
        )
        return result == 0

    def verify_send_proof(
        self: Self,
        proof: str,
        participants: list,
        sender_spending_ciphertext: str,
        amount_commitment: str,
        balance_commitment: str,
        context_hash: str,
    ) -> bool:
        """
        Verify a ConfidentialMPTSend proof using the utility layer.

        Args:
            proof: Hex string of the proof (946 bytes)
            participants: List of (pubkey, encrypted_amount) tuples as hex strings
            sender_spending_ciphertext: 132-char hex string (66-byte on-ledger balance)
            amount_commitment: 66-char hex string (33-byte Pedersen commitment)
            balance_commitment: 66-char hex string (33-byte Pedersen commitment)
            context_hash: 64-char hex string (32-byte context hash)

        Returns:
            True if proof is valid, False otherwise
        """
        # Validate lengths before the C call (untrusted proof inputs).
        proof_bytes = _hex_to_fixed_bytes(proof, 946, "proof")
        context_bytes = _hex_to_fixed_bytes(context_hash, 32, "context_hash")
        spending_bytes = _hex_to_fixed_bytes(
            sender_spending_ciphertext, 66, "sender_spending_ciphertext"
        )
        amount_commit_bytes = _hex_to_fixed_bytes(
            amount_commitment, 33, "amount_commitment"
        )
        balance_commit_bytes = _hex_to_fixed_bytes(
            balance_commitment, 33, "balance_commitment"
        )

        n_participants = len(participants)
        if not 3 <= n_participants <= 4:
            raise ValueError(
                "participants must contain 3 or 4 entries "
                "(sender, destination, issuer, [auditor])"
            )
        participants_array = ffi.new(f"mpt_confidential_participant[{n_participants}]")
        for i, (pubkey, encrypted_amount) in enumerate(participants):
            ffi.memmove(
                participants_array[i].pubkey,
                _hex_to_fixed_bytes(pubkey, 33, "participant pubkey"),
                33,
            )
            ffi.memmove(
                participants_array[i].ciphertext,
                _hex_to_fixed_bytes(encrypted_amount, 66, "participant ciphertext"),
                66,
            )

        result = lib.mpt_verify_send_proof(
            proof_bytes,
            participants_array,
            n_participants,
            spending_bytes,
            amount_commit_bytes,
            balance_commit_bytes,
            context_bytes,
        )
        return result == 0

    def create_confidential_send_proof(
        self: Self,
        sender_privkey: str,
        sender_pubkey: str,
        amount: int,
        sender_current_balance: int,
        participants: list,
        tx_blinding_factor: str,
        context_hash: str,
        amount_commitment: str,
        balance_commitment: str,
        balance_blinding: str,
        sender_balance_encrypted: str,
    ) -> str:
        """
        Generate complete proof for ConfidentialMPTSend using utility layer.

        Produces a compact AND-composed sigma proof (192 bytes) that simultaneously
        proves ciphertext equality, Pedersen commitment linkage, and balance ownership,
        followed by an aggregated Bulletproof range proof (754 bytes).
        Total proof size is fixed at 946 bytes.

        Args:
            sender_privkey: 64-char hex string of sender's private key
            sender_pubkey: 66-char hex string of sender's compressed public key
            amount: Amount being sent (uint64)
            sender_current_balance: Sender's current balance (uint64)
            participants: List of (pubkey, encrypted_amount) tuples as hex
                         strings. Must include sender, destination, issuer, and
                         optionally auditor. Each pubkey is 66 hex chars (33
                         bytes compressed); each encrypted_amount 132 hex chars.
            tx_blinding_factor: 64-char hex string of ElGamal blinding factor
            context_hash: 64-char hex string of transaction context hash
            amount_commitment: 66-char hex string of Pedersen commitment to amount
            balance_commitment: 66-char hex of Pedersen commitment to balance
            balance_blinding: 64-char hex blinding factor for balance commitment
            sender_balance_encrypted: 132-char hex of sender's balance ciphertext

        Returns:
            Hex string of complete ZKProof (946 bytes = 1892 hex chars)
        """
        # Convert inputs from hex to bytes, validating lengths before the C call.
        priv_bytes = _hex_to_fixed_bytes(sender_privkey, 32, "sender_privkey")
        pub_bytes = _hex_to_fixed_bytes(sender_pubkey, 33, "sender_pubkey")
        tx_blinding_bytes = _hex_to_fixed_bytes(
            tx_blinding_factor, 32, "tx_blinding_factor"
        )
        context_bytes = _hex_to_fixed_bytes(context_hash, 32, "context_hash")
        amount_commitment_bytes = _hex_to_fixed_bytes(
            amount_commitment, 33, "amount_commitment"
        )

        # Build participants array
        n_participants = len(participants)
        if not 3 <= n_participants <= 4:
            raise ValueError(
                "participants must contain 3 or 4 entries "
                "(sender, destination, issuer, [auditor])"
            )
        participants_array = ffi.new(f"mpt_confidential_participant[{n_participants}]")
        for i, (pubkey, encrypted_amount) in enumerate(participants):
            pubkey_bytes = _hex_to_fixed_bytes(pubkey, 33, "participant pubkey")
            enc_amt_bytes = _hex_to_fixed_bytes(
                encrypted_amount, 66, "participant ciphertext"
            )
            ffi.memmove(participants_array[i].pubkey, pubkey_bytes, 33)
            ffi.memmove(participants_array[i].ciphertext, enc_amt_bytes, 66)

        # Build balance_params
        balance_params = ffi.new("mpt_pedersen_proof_params*")
        ffi.memmove(
            balance_params.pedersen_commitment,
            _hex_to_fixed_bytes(balance_commitment, 33, "balance_commitment"),
            33,
        )
        balance_params.amount = sender_current_balance
        ffi.memmove(
            balance_params.ciphertext,
            _hex_to_fixed_bytes(
                sender_balance_encrypted, 66, "sender_balance_encrypted"
            ),
            66,
        )
        ffi.memmove(
            balance_params.blinding_factor,
            _hex_to_fixed_bytes(balance_blinding, 32, "balance_blinding"),
            32,
        )

        # Proof size: SECP256K1_COMPACT_STANDARD_PROOF_SIZE (192) +
        #             kMPT_DOUBLE_BULLETPROOF_SIZE (754) = 946
        proof_size = (
            lib.SECP256K1_COMPACT_STANDARD_PROOF_SIZE + lib.kMPT_DOUBLE_BULLETPROOF_SIZE
        )

        # Allocate proof buffer
        proof_buffer = ffi.new(f"uint8_t[{proof_size}]")
        out_len = ffi.new("size_t*")
        out_len[0] = proof_size

        # Generate proof
        result = lib.mpt_get_confidential_send_proof(
            priv_bytes,
            pub_bytes,
            amount,
            participants_array,
            n_participants,
            tx_blinding_bytes,
            context_bytes,
            amount_commitment_bytes,
            balance_params,
            proof_buffer,
            out_len,
        )

        if result != 0:
            raise RuntimeError(
                f"Failed to generate confidential send proof (error code: {result})"
            )

        actual_len = out_len[0]
        proof = bytes(ffi.buffer(proof_buffer, actual_len))
        return proof.hex().upper()

    def create_confidential_convert_back_proof(
        self: Self,
        holder_privkey: str,
        holder_pubkey: str,
        amount: int,
        current_balance: int,
        context_hash: str,
        balance_commitment: str,
        balance_blinding: str,
        holder_balance_encrypted: str,
    ) -> str:
        """
        Generate ZK proof for a ConfidentialMPTConvertBack transaction.

        Produces a compact AND-composed sigma proof (128 bytes) over the balance
        witness, followed by a single Bulletproof range proof (688 bytes) over the
        remainder commitment. Total proof size: 816 bytes.

        Args:
            holder_privkey: 64-char hex string of holder's private key
            holder_pubkey: 66-char hex string of holder's compressed public key
            amount: Amount being converted back (uint64)
            current_balance: Holder's current confidential balance (uint64)
            context_hash: 64-char hex string of transaction context hash
            balance_commitment: 66-char hex of Pedersen commitment to balance
            balance_blinding: 64-char hex blinding factor for balance commitment
            holder_balance_encrypted: 132-char hex of holder's encrypted balance

        Returns:
            Hex string of ZKProof (816 bytes = 1632 hex chars)
            Includes: Compact sigma proof (128 bytes) + Bulletproof (688 bytes)
        """
        # Convert inputs from hex to bytes, validating lengths before the C call.
        priv_bytes = _hex_to_fixed_bytes(holder_privkey, 32, "holder_privkey")
        pub_bytes = _hex_to_fixed_bytes(holder_pubkey, 33, "holder_pubkey")
        context_bytes = _hex_to_fixed_bytes(context_hash, 32, "context_hash")

        # Build balance_params
        balance_params = ffi.new("mpt_pedersen_proof_params*")
        ffi.memmove(
            balance_params.pedersen_commitment,
            _hex_to_fixed_bytes(balance_commitment, 33, "balance_commitment"),
            33,
        )
        balance_params.amount = current_balance
        ffi.memmove(
            balance_params.ciphertext,
            _hex_to_fixed_bytes(
                holder_balance_encrypted, 66, "holder_balance_encrypted"
            ),
            66,
        )
        ffi.memmove(
            balance_params.blinding_factor,
            _hex_to_fixed_bytes(balance_blinding, 32, "balance_blinding"),
            32,
        )

        # Proof size: SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE (128) +
        #             kMPT_SINGLE_BULLETPROOF_SIZE (688) = 816
        proof_size = (
            lib.SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE
            + lib.kMPT_SINGLE_BULLETPROOF_SIZE
        )
        proof_buffer = ffi.new(f"uint8_t[{proof_size}]")

        # Generate proof
        result = lib.mpt_get_convert_back_proof(
            priv_bytes,
            pub_bytes,
            context_bytes,
            amount,
            balance_params,
            proof_buffer,
        )

        if result != 0:
            raise RuntimeError(
                f"Failed to generate convert back proof (error code: {result})"
            )

        proof = bytes(ffi.buffer(proof_buffer, proof_size))
        return proof.hex().upper()

    def create_confidential_clawback_proof(
        self: Self,
        issuer_privkey: str,
        issuer_pubkey: str,
        amount: int,
        context_hash: str,
        issuer_encrypted_balance: str,
    ) -> str:
        """
        Generate ZK proof for ConfidentialMPTClawback transaction using utility layer.

        Produces a compact sigma proof that proves the issuer knows the private key
        and that the ciphertext decrypts to the specified amount.

        Args:
            issuer_privkey: 64-char hex string of issuer's private key
            issuer_pubkey: 66-char hex string of issuer's compressed public key
            amount: Amount being clawed back (uint64)
            context_hash: 64-char hex string of transaction context hash
            issuer_encrypted_balance: 132-char hex of issuer's encrypted balance

        Returns:
            Hex string of ZKProof (SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE bytes)
        """
        # Convert inputs from hex to bytes, validating lengths before the C call.
        priv_bytes = _hex_to_fixed_bytes(issuer_privkey, 32, "issuer_privkey")
        pub_bytes = _hex_to_fixed_bytes(issuer_pubkey, 33, "issuer_pubkey")
        context_bytes = _hex_to_fixed_bytes(context_hash, 32, "context_hash")
        encrypted_balance_bytes = _hex_to_fixed_bytes(
            issuer_encrypted_balance, 66, "issuer_encrypted_balance"
        )

        # Allocate proof buffer
        proof_size = lib.SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE
        proof_buffer = ffi.new(f"uint8_t[{proof_size}]")

        # Generate proof
        result = lib.mpt_get_clawback_proof(
            priv_bytes,
            pub_bytes,
            context_bytes,
            amount,
            encrypted_balance_bytes,
            proof_buffer,
        )

        if result != 0:
            raise RuntimeError(
                f"Failed to generate clawback proof (error code: {result})"
            )

        proof = bytes(ffi.buffer(proof_buffer, proof_size))
        return proof.hex().upper()
