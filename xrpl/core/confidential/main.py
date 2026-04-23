"""
Main MPTCrypto class for confidential MPT operations.

This module provides the high-level Python API for mpt-crypto operations
by wrapping the functional modules into a single class interface.
"""

from typing import Optional, Tuple

from xrpl.core.confidential import (
    commitments,
    encryption,
    keypair,
)
from xrpl.core.confidential.crypto_bindings import (
    SECP256K1_CONTEXT_SIGN,
    SECP256K1_CONTEXT_VERIFY,
    ffi,
    lib,
)
from xrpl.core.confidential.encryption import (
    BLINDING_FACTOR_SIZE,
    PUBKEY_COMPRESSED_SIZE,
)

# Re-export size constants
from xrpl.core.confidential.keypair import (
    CONTEXT_ID_SIZE,
    PRIVKEY_SIZE,
    SCHNORR_PROOF_SIZE,
)
ACCOUNT_ID_SIZE = 20
MPT_ISSUANCE_ID_SIZE = 24

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

    def __init__(self):
        """Initialize the secp256k1 context."""
        self.ctx = lib.secp256k1_context_create(
            SECP256K1_CONTEXT_SIGN | SECP256K1_CONTEXT_VERIFY
        )
        if self.ctx == ffi.NULL:
            raise RuntimeError("Failed to create secp256k1 context")

    def __del__(self):
        """Clean up the secp256k1 context."""
        if hasattr(self, "ctx") and self.ctx != ffi.NULL:
            lib.secp256k1_context_destroy(self.ctx)

    # Keypair generation and Schnorr PoK
    def generate_keypair(self) -> Tuple[str, str]:
        """Generate an ElGamal keypair."""
        return keypair.generate_keypair(self.ctx)

    def generate_keypair_with_pok(
        self, context_id: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """Generate an ElGamal keypair with a Schnorr proof of knowledge."""
        return keypair.generate_keypair_with_pok(self.ctx, context_id)

    def generate_pok(
        self, privkey: str, pubkey_uncompressed: str, context_id: str
    ) -> str:
        """Generate a Schnorr proof of knowledge of the secret key."""
        return keypair.generate_pok(self.ctx, privkey, pubkey_uncompressed, context_id)

    def verify_pok(self, pubkey_uncompressed: str, proof: str, context_id: str) -> bool:
        """Verify a Schnorr proof of knowledge of secret key."""
        return keypair.verify_pok(self.ctx, pubkey_uncompressed, proof, context_id)

    # Encryption/Decryption
    def encrypt(
        self,
        pubkey_uncompressed: str,
        amount: int,
        blinding_factor: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        """Encrypt an amount using ElGamal encryption."""
        return encryption.encrypt(
            self.ctx, pubkey_uncompressed, amount, blinding_factor
        )

    def decrypt(self, privkey: str, c1: str, c2: str) -> int:
        """Decrypt an ElGamal ciphertext."""
        return encryption.decrypt(self.ctx, privkey, c1, c2)

    # Commitments and Bulletproofs
    def create_pedersen_commitment(self, amount: int, blinding_factor: str) -> str:
        """Create a Pedersen commitment: PC = amount*G + blinding_factor*H"""
        return commitments.create_pedersen_commitment(self.ctx, amount, blinding_factor)

    def create_bulletproof(
        self, amount: int, blinding_factor: str, pk_base_uncompressed: str
    ) -> str:
        """Create a Bulletproof range proof."""
        return commitments.create_bulletproof(
            self.ctx, amount, blinding_factor, pk_base_uncompressed
        )

    def verify_bulletproof(
        self, proof: str, commitment: str, pk_base_uncompressed: str
    ) -> bool:
        """Verify a Bulletproof range proof."""
        return commitments.verify_bulletproof(
            self.ctx, proof, commitment, pk_base_uncompressed
        )

    # Verify proofs using utility layer
    def verify_clawback_proof(
        self,
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
        proof_bytes = bytes.fromhex(proof)
        pubkey_bytes = bytes.fromhex(pubkey_compressed)
        ciphertext_bytes = bytes.fromhex(ciphertext)
        context_bytes = bytes.fromhex(context_hash)

        result = lib.mpt_verify_clawback_proof(
            proof_bytes, amount, pubkey_bytes, ciphertext_bytes, context_bytes
        )
        return result == 0

    def verify_convert_back_proof(
        self,
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
        proof_bytes = bytes.fromhex(proof)
        pubkey_bytes = bytes.fromhex(pubkey_compressed)
        ciphertext_bytes = bytes.fromhex(ciphertext)
        commitment_bytes = bytes.fromhex(balance_commitment)
        context_bytes = bytes.fromhex(context_hash)

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
        self,
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
        proof_bytes = bytes.fromhex(proof)
        context_bytes = bytes.fromhex(context_hash)
        spending_bytes = bytes.fromhex(sender_spending_ciphertext)
        amount_commit_bytes = bytes.fromhex(amount_commitment)
        balance_commit_bytes = bytes.fromhex(balance_commitment)

        n_participants = len(participants)
        participants_array = ffi.new(f"mpt_confidential_participant[{n_participants}]")
        for i, (pubkey, encrypted_amount) in enumerate(participants):
            ffi.memmove(participants_array[i].pubkey, bytes.fromhex(pubkey), 33)
            ffi.memmove(
                participants_array[i].ciphertext, bytes.fromhex(encrypted_amount), 66
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
        self,
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
            participants: List of (pubkey, encrypted_amount) tuples as hex strings.
                         Must include sender, destination, issuer, and optionally auditor.
                         Each pubkey is 66 hex chars (33 bytes compressed)
                         Each encrypted_amount is 132 hex chars (66 bytes)
            tx_blinding_factor: 64-char hex string of ElGamal blinding factor
            context_hash: 64-char hex string of transaction context hash
            amount_commitment: 66-char hex string of Pedersen commitment to amount
            balance_commitment: 66-char hex string of Pedersen commitment to balance
            balance_blinding: 64-char hex string of blinding factor for balance commitment
            sender_balance_encrypted: 132-char hex string of sender's current balance ciphertext

        Returns:
            Hex string of complete ZKProof (946 bytes = 1892 hex chars)
        """
        # Convert inputs from hex to bytes
        priv_bytes = bytes.fromhex(sender_privkey)
        pub_bytes = bytes.fromhex(sender_pubkey)
        tx_blinding_bytes = bytes.fromhex(tx_blinding_factor)
        context_bytes = bytes.fromhex(context_hash)
        amount_commitment_bytes = bytes.fromhex(amount_commitment)

        # Build participants array
        n_participants = len(participants)
        participants_array = ffi.new(f"mpt_confidential_participant[{n_participants}]")
        for i, (pubkey, encrypted_amount) in enumerate(participants):
            pubkey_bytes = bytes.fromhex(pubkey)
            enc_amt_bytes = bytes.fromhex(encrypted_amount)
            ffi.memmove(participants_array[i].pubkey, pubkey_bytes, 33)
            ffi.memmove(participants_array[i].ciphertext, enc_amt_bytes, 66)

        # Build balance_params
        balance_params = ffi.new("mpt_pedersen_proof_params*")
        ffi.memmove(
            balance_params.pedersen_commitment, bytes.fromhex(balance_commitment), 33
        )
        balance_params.amount = sender_current_balance
        ffi.memmove(
            balance_params.ciphertext,
            bytes.fromhex(sender_balance_encrypted),
            66,
        )
        ffi.memmove(balance_params.blinding_factor, bytes.fromhex(balance_blinding), 32)

        # Proof size: SECP256K1_COMPACT_STANDARD_PROOF_SIZE (192) +
        #             kMPT_DOUBLE_BULLETPROOF_SIZE (754) = 946
        proof_size = lib.SECP256K1_COMPACT_STANDARD_PROOF_SIZE + lib.kMPT_DOUBLE_BULLETPROOF_SIZE

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
        self,
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
        Generate ZK proof for ConfidentialMPTConvertBack transaction using utility layer.

        Produces a compact AND-composed sigma proof (128 bytes) over the balance
        witness, followed by a single Bulletproof range proof (688 bytes) over the
        remainder commitment. Total proof size: 816 bytes.

        Args:
            holder_privkey: 64-char hex string of holder's private key
            holder_pubkey: 66-char hex string of holder's compressed public key
            amount: Amount being converted back (uint64)
            current_balance: Holder's current confidential balance (uint64)
            context_hash: 64-char hex string of transaction context hash
            balance_commitment: 66-char hex string of Pedersen commitment to balance
            balance_blinding: 64-char hex string of blinding factor for balance commitment
            holder_balance_encrypted: 132-char hex string of holder's encrypted balance

        Returns:
            Hex string of ZKProof (816 bytes = 1632 hex chars)
            Includes: Compact sigma proof (128 bytes) + Bulletproof (688 bytes)
        """
        # Convert inputs from hex to bytes
        priv_bytes = bytes.fromhex(holder_privkey)
        pub_bytes = bytes.fromhex(holder_pubkey)
        context_bytes = bytes.fromhex(context_hash)

        # Build balance_params
        balance_params = ffi.new("mpt_pedersen_proof_params*")
        ffi.memmove(
            balance_params.pedersen_commitment, bytes.fromhex(balance_commitment), 33
        )
        balance_params.amount = current_balance
        ffi.memmove(
            balance_params.ciphertext,
            bytes.fromhex(holder_balance_encrypted),
            66,
        )
        ffi.memmove(balance_params.blinding_factor, bytes.fromhex(balance_blinding), 32)

        # Proof size: SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE (128) +
        #             kMPT_SINGLE_BULLETPROOF_SIZE (688) = 816
        proof_size = lib.SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE + lib.kMPT_SINGLE_BULLETPROOF_SIZE
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
        self,
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
            issuer_encrypted_balance: 132-char hex string of issuer's encrypted balance from ledger

        Returns:
            Hex string of ZKProof (SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE bytes)
        """
        # Convert inputs from hex to bytes
        priv_bytes = bytes.fromhex(issuer_privkey)
        pub_bytes = bytes.fromhex(issuer_pubkey)
        context_bytes = bytes.fromhex(context_hash)
        encrypted_balance_bytes = bytes.fromhex(issuer_encrypted_balance)

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
