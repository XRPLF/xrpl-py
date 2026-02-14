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
    PUBKEY_UNCOMPRESSED_SIZE,
    SCHNORR_PROOF_SIZE,
)
from xrpl.core.confidential.link_proofs import ACCOUNT_ID_SIZE, MPT_ISSUANCE_ID_SIZE

# Export size constants
__all__ = [
    "MPTCrypto",
    "PRIVKEY_SIZE",
    "PUBKEY_UNCOMPRESSED_SIZE",
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
        blinding_factor: str,
        context_id: str,
    ) -> str:
        """Create an equality proof for ConfidentialMPTClawback."""
        return plaintext_proofs.create_equality_plaintext_proof(
            self.ctx, pk_uncompressed, c2, c1, amount, blinding_factor, context_id
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
