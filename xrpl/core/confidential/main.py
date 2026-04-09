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
    link_proofs,
    plaintext_proofs,
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
from xrpl.core.confidential.link_proofs import ACCOUNT_ID_SIZE, MPT_ISSUANCE_ID_SIZE

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

    # Link Proofs
    def create_elgamal_pedersen_link_proof(  # noqa: PLR0913
        self,
        c1: str,
        c2: str,
        pk_uncompressed: str,
        pedersen_commitment: str,
        amount: int,
        amount_blinding: str,
        pedersen_blinding: str,
        context_id: str,
    ) -> str:
        """Create an ElGamal-Pedersen link proof."""
        return link_proofs.create_elgamal_pedersen_link_proof(
            self.ctx,
            c1,
            c2,
            pk_uncompressed,
            pedersen_commitment,
            amount,
            amount_blinding,
            pedersen_blinding,
            context_id,
        )

    def verify_elgamal_pedersen_link_proof(
        self,
        proof: str,
        c1: str,
        c2: str,
        pk_uncompressed: str,
        pedersen_commitment: str,
        context_id: str,
    ) -> bool:
        """Verify an ElGamal-Pedersen link proof."""
        return link_proofs.verify_elgamal_pedersen_link_proof(
            self.ctx, proof, c1, c2, pk_uncompressed, pedersen_commitment, context_id
        )

    def create_balance_link_proof(  # noqa: PLR0913
        self,
        pk_uncompressed: str,
        c2: str,
        c1: str,
        pedersen_commitment: str,
        amount: int,
        private_key: str,
        pedersen_blinding: str,
        context_id: str,
    ) -> str:
        """Create a balance link proof (uses SWAPPED parameter order)."""
        return link_proofs.create_balance_link_proof(
            self.ctx,
            pk_uncompressed,
            c2,
            c1,
            pedersen_commitment,
            amount,
            private_key,
            pedersen_blinding,
            context_id,
        )

    # Equality and Same Plaintext Proofs
    def create_equality_plaintext_proof(
        self,
        pk_uncompressed: str,
        c2: str,
        c1: str,
        amount: int,
        private_key: str,
        context_id: str,
    ) -> str:
        """Create an equality proof for ConfidentialMPTClawback."""
        return plaintext_proofs.create_equality_plaintext_proof(
            self.ctx, pk_uncompressed, c2, c1, amount, private_key, context_id
        )

    def verify_equality_plaintext_proof(
        self,
        proof: str,
        pk_uncompressed: str,
        c2: str,
        c1: str,
        amount: int,
        context_id: str,
    ) -> bool:
        """Verify an equality plaintext proof (for ConfidentialMPTClawback)."""
        return plaintext_proofs.verify_equality_plaintext_proof(
            self.ctx, proof, pk_uncompressed, c2, c1, amount, context_id
        )

    def create_same_plaintext_proof_multi(
        self,
        amount: int,
        ciphertexts: list,
        context_id: str,
    ) -> str:
        """Create a proof that multiple ciphertexts encrypt the same amount."""
        return plaintext_proofs.create_same_plaintext_proof_multi(
            self.ctx, amount, ciphertexts, context_id
        )

    def verify_same_plaintext_proof_multi(
        self,
        proof: str,
        ciphertexts: list,
        context_id: str,
    ) -> bool:
        """Verify a proof that multiple ciphertexts encrypt the same amount."""
        return plaintext_proofs.verify_same_plaintext_proof_multi(
            self.ctx, proof, ciphertexts, context_id
        )

    def create_confidential_send_proof(
        self,
        sender_privkey: str,
        amount: int,
        sender_current_balance: int,
        recipients: list,
        tx_blinding_factor: str,
        context_hash: str,
        amount_commitment: str,
        amount_blinding: str,
        sender_encrypted_amount: str,
        balance_commitment: str,
        balance_blinding: str,
        sender_balance_encrypted: str,
    ) -> str:
        """
        Generate complete proof for ConfidentialMPTSend using utility layer.

        This generates the complete ZKProof including:
        - Multi-ciphertext equality proof
        - Pedersen linkage proofs (amount and balance)
        - Double bulletproof (range proofs)

        Args:
            sender_privkey: 64-char hex string of sender's private key
            amount: Amount being sent (uint64)
            recipients: List of (pubkey, encrypted_amount) tuples as hex strings
                       Each pubkey is 66 hex chars (33 bytes compressed)
                       Each encrypted_amount is 132 hex chars (66 bytes)
            tx_blinding_factor: 64-char hex string of ElGamal blinding factor
            context_hash: 64-char hex string of transaction context hash
            amount_commitment: 66-char hex string of Pedersen commitment to amount
            amount_blinding: 64-char hex string of blinding factor for amount commitment
            sender_encrypted_amount: 132-char hex string of sender's encrypted amount
            balance_commitment: 66-char hex string of Pedersen commitment to balance
            balance_blinding: 64-char hex string of blinding factor for balance commitment
            sender_balance_encrypted: 132-char hex string of sender's current balance

        Returns:
            Hex string of complete ZKProof (approximately 1503 bytes = 3006 hex chars)
        """
        # Convert inputs from hex to bytes
        priv_bytes = bytes.fromhex(sender_privkey)
        tx_blinding_bytes = bytes.fromhex(tx_blinding_factor)
        context_bytes = bytes.fromhex(context_hash)

        # Build recipients array
        n_recipients = len(recipients)
        recipients_array = ffi.new(f"mpt_confidential_participant[{n_recipients}]")
        for i, (pubkey, encrypted_amount) in enumerate(recipients):
            pubkey_bytes = bytes.fromhex(pubkey)
            enc_amt_bytes = bytes.fromhex(encrypted_amount)
            ffi.memmove(recipients_array[i].pubkey, pubkey_bytes, 33)
            ffi.memmove(recipients_array[i].ciphertext, enc_amt_bytes, 66)

        # Build amount_params
        amount_params = ffi.new("mpt_pedersen_proof_params*")
        ffi.memmove(
            amount_params.pedersen_commitment, bytes.fromhex(amount_commitment), 33
        )
        amount_params.amount = amount
        ffi.memmove(
            amount_params.ciphertext, bytes.fromhex(sender_encrypted_amount), 66
        )
        ffi.memmove(amount_params.blinding_factor, bytes.fromhex(amount_blinding), 32)

        # Build balance_params
        # NOTE: sender_balance_encrypted should be a fresh encryption of the current balance
        # using balance_blinding, NOT the balance from the ledger
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

        # Get proof size
        proof_size = lib.get_confidential_send_proof_size(n_recipients)

        # Allocate proof buffer
        proof_buffer = ffi.new(f"uint8_t[{proof_size}]")
        out_len = ffi.new("size_t*")
        out_len[0] = proof_size

        # Generate proof
        result = lib.mpt_get_confidential_send_proof(
            priv_bytes,
            amount,
            recipients_array,
            n_recipients,
            tx_blinding_bytes,
            context_bytes,
            amount_params,
            balance_params,
            proof_buffer,
            out_len,
        )

        if result != 0:
            raise RuntimeError(
                f"Failed to generate confidential send proof (error code: {result})"
            )

        # Return the proof
        # Note: The utility layer currently returns an incomplete proof (missing bulletproof)
        # This will be fixed in an upcoming mpt-crypto release
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
            Hex string of ZKProof (883 bytes = 1766 hex chars)
            Includes: Pedersen linkage proof (195 bytes) + Bulletproof (688 bytes)
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

        # Allocate proof buffer (195 + 688 = 883 bytes)
        proof_size = 195 + 688
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

        Args:
            issuer_privkey: 64-char hex string of issuer's private key
            issuer_pubkey: 66-char hex string of issuer's compressed public key
            amount: Amount being clawed back (uint64)
            context_hash: 64-char hex string of transaction context hash
            issuer_encrypted_balance: 132-char hex string of issuer's encrypted balance from ledger

        Returns:
            Hex string of ZKProof (98 bytes = 196 hex chars)
        """
        # Convert inputs from hex to bytes
        priv_bytes = bytes.fromhex(issuer_privkey)
        pub_bytes = bytes.fromhex(issuer_pubkey)
        context_bytes = bytes.fromhex(context_hash)
        encrypted_balance_bytes = bytes.fromhex(issuer_encrypted_balance)

        # Allocate proof buffer (98 bytes for equality proof)
        proof_buffer = ffi.new("uint8_t[98]")

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

        proof = bytes(ffi.buffer(proof_buffer, 98))
        return proof.hex().upper()
