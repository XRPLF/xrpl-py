"""
Python bindings for mpt-crypto C library using cffi.

This module provides a clean Python API for the mpt-crypto library,
which implements cryptographic operations for confidential MPT transactions.
"""

import os
import secrets
import sys
from typing import Optional, Tuple

# Add the current directory to sys.path to allow importing the compiled C extension
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

try:
    from _mpt_crypto import ffi, lib

    MPT_CRYPTO_AVAILABLE = True
except ImportError as exc:
    MPT_CRYPTO_AVAILABLE = False
    _import_error = exc

    # Provide a helpful error message
    def _raise_not_available(*args, **kwargs):
        raise ImportError(
            "\n"
            "Confidential MPT support is not available.\n"
            "\n"
            "To enable confidential MPT features, run the setup script:\n"
            "  python -m xrpl.core.confidential.setup\n"
            "\n"
            "Or manually build the C extension:\n"
            "  python xrpl/core/confidential/build_mpt_crypto.py\n"
            "\n"
            f"Original error: {_import_error}\n"
        ) from _import_error

    # Create dummy objects that will raise the error when accessed
    class _DummyFFI:
        def __getattr__(self, name):
            _raise_not_available()

    class _DummyLib:
        def __getattr__(self, name):
            _raise_not_available()

    ffi = _DummyFFI()
    lib = _DummyLib()

# Constants (only set if library is available)
if MPT_CRYPTO_AVAILABLE:
    SECP256K1_CONTEXT_SIGN = lib.SECP256K1_CONTEXT_SIGN
    SECP256K1_CONTEXT_VERIFY = lib.SECP256K1_CONTEXT_VERIFY
    SECP256K1_EC_COMPRESSED = lib.SECP256K1_EC_COMPRESSED
    SECP256K1_EC_UNCOMPRESSED = lib.SECP256K1_EC_UNCOMPRESSED
else:
    SECP256K1_CONTEXT_SIGN = None
    SECP256K1_CONTEXT_VERIFY = None
    SECP256K1_EC_COMPRESSED = None
    SECP256K1_EC_UNCOMPRESSED = None

# Size constants
PRIVKEY_SIZE = 32
PUBKEY_UNCOMPRESSED_SIZE = 64
PUBKEY_COMPRESSED_SIZE = 33
SCHNORR_PROOF_SIZE = 65
BLINDING_FACTOR_SIZE = 32
CONTEXT_ID_SIZE = 32
ACCOUNT_ID_SIZE = 20
MPT_ISSUANCE_ID_SIZE = 24
EQUALITY_PROOF_SIZE = 98
SAME_PLAINTEXT_PROOF_SIZE = 261


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

    def generate_keypair(self) -> Tuple[str, str]:
        """
        Generate an ElGamal keypair.

        Returns:
            Tuple of (private_key, public_key_uncompressed)
            - private_key: 64-char hex string (32 bytes)
            - public_key_uncompressed: 128-char hex string (64 bytes, X || Y coordinates)
        """
        privkey = ffi.new("unsigned char[32]")
        pubkey = ffi.new("secp256k1_pubkey *")

        result = lib.secp256k1_elgamal_generate_keypair(self.ctx, privkey, pubkey)
        if result != 1:
            raise RuntimeError("Failed to generate keypair")

        # Serialize public key to uncompressed format (64 bytes)
        output = ffi.new("unsigned char[65]")  # 65 for uncompressed with prefix
        outputlen = ffi.new("size_t *", 65)

        result = lib.secp256k1_ec_pubkey_serialize(
            self.ctx, output, outputlen, pubkey, SECP256K1_EC_UNCOMPRESSED
        )
        if result != 1:
            raise RuntimeError("Failed to serialize public key")

        # Return private key and public key WITHOUT the 0x04 prefix (just X||Y)
        privkey_bytes = bytes(privkey[0:32])
        pubkey_bytes = bytes(output[1:65])  # Skip the 0x04 prefix

        # Convert to hex strings
        return privkey_bytes.hex().upper(), pubkey_bytes.hex().upper()

    def generate_keypair_with_pok(
        self, context_id: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Generate an ElGamal keypair with proof of knowledge of secret key.

        Args:
            context_id: 64-char hex string (32 bytes, defaults to zeros for registration)

        Returns:
            Tuple of (private_key, public_key_uncompressed, schnorr_proof)
            - private_key: 64-char hex string (32 bytes)
            - public_key_uncompressed: 128-char hex string (64 bytes, X || Y)
            - schnorr_proof: 130-char hex string (65 bytes, 33 bytes T + 32 bytes s)
        """
        if context_id is None:
            context_id_bytes = b"\x00" * CONTEXT_ID_SIZE
        else:
            context_id_bytes = bytes.fromhex(context_id)
            if len(context_id_bytes) != CONTEXT_ID_SIZE:
                raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

        # Generate keypair (returns hex strings)
        privkey, pubkey = self.generate_keypair()

        # Generate proof (returns hex string)
        context_id_hex = (
            context_id if context_id is not None else "00" * CONTEXT_ID_SIZE
        )
        proof = self.generate_pok(privkey, pubkey, context_id_hex)

        return privkey, pubkey, proof

    def generate_pok(
        self, privkey: str, pubkey_uncompressed: str, context_id: str
    ) -> str:
        """
        Generate a Schnorr proof of knowledge of secret key.

        Args:
            privkey: 64-char hex string (32-byte private key)
            pubkey_uncompressed: 128-char hex string (64-byte public key, X || Y)
            context_id: 64-char hex string (32-byte context ID)

        Returns:
            130-char hex string (65-byte Schnorr proof: 33 bytes T + 32 bytes s)
        """
        # Convert hex strings to bytes
        privkey_bytes = bytes.fromhex(privkey)
        pubkey_bytes = bytes.fromhex(pubkey_uncompressed)
        context_id_bytes = bytes.fromhex(context_id)

        if len(privkey_bytes) != PRIVKEY_SIZE:
            raise ValueError(f"privkey must be {PRIVKEY_SIZE} bytes")
        if len(pubkey_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
            raise ValueError(f"pubkey must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")
        if len(context_id_bytes) != CONTEXT_ID_SIZE:
            raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

        # Parse public key (add 0x04 prefix for uncompressed format)
        pubkey_with_prefix = b"\x04" + pubkey_bytes
        pubkey = ffi.new("secp256k1_pubkey *")
        result = lib.secp256k1_ec_pubkey_parse(self.ctx, pubkey, pubkey_with_prefix, 65)
        if result != 1:
            raise RuntimeError("Failed to parse public key")

        # Generate proof
        proof = ffi.new("unsigned char[65]")
        result = lib.secp256k1_mpt_pok_sk_prove(
            self.ctx, proof, pubkey, privkey_bytes, context_id_bytes
        )
        if result != 1:
            raise RuntimeError("Failed to generate proof of knowledge")

        return bytes(proof[0:65]).hex().upper()

    def verify_pok(self, pubkey_uncompressed: str, proof: str, context_id: str) -> bool:
        """
        Verify a Schnorr proof of knowledge of secret key.

        Args:
            pubkey_uncompressed: 128-char hex string (64-byte public key, X || Y)
            proof: 130-char hex string (65-byte Schnorr proof)
            context_id: 64-char hex string (32-byte context ID)

        Returns:
            True if proof is valid, False otherwise
        """
        # Convert hex strings to bytes
        pubkey_bytes = bytes.fromhex(pubkey_uncompressed)
        proof_bytes = bytes.fromhex(proof)
        context_id_bytes = bytes.fromhex(context_id)

        if len(pubkey_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
            raise ValueError(f"pubkey must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")
        if len(proof_bytes) != SCHNORR_PROOF_SIZE:
            raise ValueError(f"proof must be {SCHNORR_PROOF_SIZE} bytes")
        if len(context_id_bytes) != CONTEXT_ID_SIZE:
            raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

        # Parse public key (add 0x04 prefix for uncompressed format)
        pubkey_with_prefix = b"\x04" + pubkey_bytes
        pubkey = ffi.new("secp256k1_pubkey *")
        result = lib.secp256k1_ec_pubkey_parse(self.ctx, pubkey, pubkey_with_prefix, 65)
        if result != 1:
            raise RuntimeError("Failed to parse public key")

        # Verify proof
        result = lib.secp256k1_mpt_pok_sk_verify(
            self.ctx, proof_bytes, pubkey, context_id_bytes
        )
        return result == 1

    def encrypt(
        self,
        pubkey_uncompressed: str,
        amount: int,
        blinding_factor: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        """
        Encrypt an amount using ElGamal encryption.

        Args:
            pubkey_uncompressed: 128-char hex string (64-byte public key, X || Y)
            amount: Amount to encrypt (uint64)
            blinding_factor: 64-char hex string (32-byte blinding factor, random if None)

        Returns:
            Tuple of (c1, c2, blinding_factor)
            - c1: 66-char hex string (33-byte compressed point)
            - c2: 66-char hex string (33-byte compressed point)
            - blinding_factor: 64-char hex string (32 bytes, the one used for encryption)
        """
        # Convert hex strings to bytes
        pubkey_bytes = bytes.fromhex(pubkey_uncompressed)

        if len(pubkey_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
            raise ValueError(f"pubkey must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")
        if amount < 0 or amount > 0xFFFFFFFFFFFFFFFF:
            raise ValueError("amount must be a valid uint64")

        # Generate random blinding factor if not provided
        if blinding_factor is None:
            blinding_bytes = secrets.token_bytes(BLINDING_FACTOR_SIZE)
        else:
            blinding_bytes = bytes.fromhex(blinding_factor)
            if len(blinding_bytes) != BLINDING_FACTOR_SIZE:
                raise ValueError(
                    f"blinding_factor must be {BLINDING_FACTOR_SIZE} bytes"
                )

        # Parse public key
        pubkey_with_prefix = b"\x04" + pubkey_bytes
        pubkey = ffi.new("secp256k1_pubkey *")
        result = lib.secp256k1_ec_pubkey_parse(self.ctx, pubkey, pubkey_with_prefix, 65)
        if result != 1:
            raise RuntimeError("Failed to parse public key")

        # Encrypt
        c1 = ffi.new("secp256k1_pubkey *")
        c2 = ffi.new("secp256k1_pubkey *")
        result = lib.secp256k1_elgamal_encrypt(
            self.ctx, c1, c2, pubkey, amount, blinding_bytes
        )
        if result != 1:
            raise RuntimeError("Failed to encrypt")

        # Serialize c1 and c2 to compressed format
        c1_bytes = self._serialize_pubkey(c1, compressed=True)
        c2_bytes = self._serialize_pubkey(c2, compressed=True)

        # Return hex strings
        return (
            c1_bytes.hex().upper(),
            c2_bytes.hex().upper(),
            blinding_bytes.hex().upper(),
        )

    def _serialize_pubkey(self, pubkey, compressed: bool = True) -> bytes:
        """Serialize a secp256k1_pubkey to bytes."""
        if compressed:
            output = ffi.new("unsigned char[33]")
            outputlen = ffi.new("size_t *", 33)
            flags = SECP256K1_EC_COMPRESSED
        else:
            output = ffi.new("unsigned char[65]")
            outputlen = ffi.new("size_t *", 65)
            flags = SECP256K1_EC_UNCOMPRESSED

        result = lib.secp256k1_ec_pubkey_serialize(
            self.ctx, output, outputlen, pubkey, flags
        )
        if result != 1:
            raise RuntimeError("Failed to serialize public key")

        if compressed:
            return bytes(output[0:33])
        return bytes(output[1:65])  # Skip 0x04 prefix

    def decrypt(self, privkey: str, c1: str, c2: str) -> int:
        """
        Decrypt an ElGamal ciphertext.

        Args:
            privkey: 64-char hex string (32-byte private key)
            c1: 66-char hex string (33-byte compressed point)
            c2: 66-char hex string (33-byte compressed point)

        Returns:
            Decrypted amount (uint64)
        """
        # Convert hex strings to bytes
        privkey_bytes = bytes.fromhex(privkey)
        c1_bytes = bytes.fromhex(c1)
        c2_bytes = bytes.fromhex(c2)

        if len(privkey_bytes) != PRIVKEY_SIZE:
            raise ValueError(f"privkey must be {PRIVKEY_SIZE} bytes")
        if len(c1_bytes) != PUBKEY_COMPRESSED_SIZE:
            raise ValueError(f"c1 must be {PUBKEY_COMPRESSED_SIZE} bytes")
        if len(c2_bytes) != PUBKEY_COMPRESSED_SIZE:
            raise ValueError(f"c2 must be {PUBKEY_COMPRESSED_SIZE} bytes")

        # Parse c1 and c2
        c1_pk = ffi.new("secp256k1_pubkey *")
        c2_pk = ffi.new("secp256k1_pubkey *")

        result = lib.secp256k1_ec_pubkey_parse(self.ctx, c1_pk, c1_bytes, 33)
        if result != 1:
            raise RuntimeError("Failed to parse c1")

        result = lib.secp256k1_ec_pubkey_parse(self.ctx, c2_pk, c2_bytes, 33)
        if result != 1:
            raise RuntimeError("Failed to parse c2")

        # Decrypt
        amount = ffi.new("uint64_t *")
        result = lib.secp256k1_elgamal_decrypt(
            self.ctx, amount, c1_pk, c2_pk, privkey_bytes
        )
        if result != 1:
            raise RuntimeError("Failed to decrypt")

        return int(amount[0])

    def create_pedersen_commitment(self, amount: int, blinding_factor: str) -> str:
        """
        Create a Pedersen commitment: PC = amount*G + blinding_factor*H

        Args:
            amount: The amount to commit to
            blinding_factor: 64-char hex string (32-byte blinding factor rho)

        Returns:
            128-char hex string (64-byte uncompressed commitment point, X + Y coordinates)
        """
        # Convert hex string to bytes
        blinding_bytes = bytes.fromhex(blinding_factor)

        if len(blinding_bytes) != 32:
            raise ValueError("blinding_factor must be 32 bytes")

        commitment = ffi.new("secp256k1_pubkey *")
        result = lib.secp256k1_mpt_pedersen_commit(
            self.ctx, commitment, amount, blinding_bytes
        )
        if result != 1:
            raise RuntimeError("Failed to create Pedersen commitment")

        # Serialize to uncompressed format (65 bytes: 0x04 prefix + X + Y)
        output = ffi.new("unsigned char[65]")
        outputlen = ffi.new("size_t *", 65)
        result = lib.secp256k1_ec_pubkey_serialize(
            self.ctx, output, outputlen, commitment, SECP256K1_EC_UNCOMPRESSED
        )
        if result != 1:
            raise RuntimeError("Failed to serialize commitment")

        # Return only X and Y coordinates (skip the 0x04 prefix) as hex string
        return bytes(output[1:65]).hex().upper()

    def create_bulletproof(
        self, amount: int, blinding_factor: str, pk_base_uncompressed: str
    ) -> str:
        """
        Create a Bulletproof range proof for an amount.

        Args:
            amount: The amount to prove is in valid range
            blinding_factor: 64-char hex string (32-byte blinding factor used in commitment)
            pk_base_uncompressed: 128-char hex string (64-byte public key, H generator)

        Returns:
            Variable-length hex string (Bulletproof, typically ~600-700 bytes)
        """
        # Convert hex strings to bytes
        blinding_bytes = bytes.fromhex(blinding_factor)
        pk_base_bytes = bytes.fromhex(pk_base_uncompressed)

        if len(blinding_bytes) != 32:
            raise ValueError("blinding_factor must be 32 bytes")
        if len(pk_base_bytes) != 64:
            raise ValueError("pk_base must be 64 bytes")

        # Parse public key
        pk_base_with_prefix = b"\x04" + pk_base_bytes
        pk_base = ffi.new("secp256k1_pubkey *")
        result = lib.secp256k1_ec_pubkey_parse(
            self.ctx, pk_base, pk_base_with_prefix, 65
        )
        if result != 1:
            raise RuntimeError("Failed to parse pk_base")

        # Allocate buffer for proof (max size ~1024 bytes)
        proof_out = ffi.new("unsigned char[1024]")
        proof_len = ffi.new("size_t *", 1024)

        # Generate proof (proof_type=64 for 64-bit range)
        result = lib.secp256k1_bulletproof_prove(
            self.ctx, proof_out, proof_len, amount, blinding_bytes, pk_base, 64
        )
        if result != 1:
            raise RuntimeError("Failed to create Bulletproof")

        return bytes(proof_out[0 : proof_len[0]]).hex().upper()

    def create_elgamal_pedersen_link_proof(  # noqa: PLR0913
        self,
        c1: str,
        c2: str,
        pk_uncompressed: str,
        pedersen_commitment: str,
        amount: int,
        elgamal_blinding: str,
        pedersen_blinding: str,
        context_id: str,
    ) -> str:
        """
        Create a proof linking an ElGamal ciphertext to a Pedersen commitment.

        Proves knowledge of (amount, r, rho) such that:
        - C1 = r*G, C2 = amount*G + r*Pk (ElGamal)
        - PCm = amount*G + rho*H (Pedersen)

        Args:
            c1: 66-char hex string (33-byte compressed C1 point)
            c2: 66-char hex string (33-byte compressed C2 point)
            pk_uncompressed: 128-char hex string (64-byte public key)
            pedersen_commitment: 128-char hex string (64-byte Pedersen commitment, X + Y)
            amount: The plaintext amount
            elgamal_blinding: 64-char hex string (32-byte ElGamal blinding factor r)
            pedersen_blinding: 64-char hex string (32-byte Pedersen blinding factor rho)
            context_id: 64-char hex string (32-byte transaction context ID)

        Returns:
            390-char hex string (195-byte link proof)
        """
        # Convert hex strings to bytes
        c1_bytes = bytes.fromhex(c1)
        c2_bytes = bytes.fromhex(c2)
        pk_bytes = bytes.fromhex(pk_uncompressed)
        pcm_bytes = bytes.fromhex(pedersen_commitment)
        elgamal_blinding_bytes = bytes.fromhex(elgamal_blinding)
        pedersen_blinding_bytes = bytes.fromhex(pedersen_blinding)
        context_id_bytes = bytes.fromhex(context_id)

        if len(c1_bytes) != 33 or len(c2_bytes) != 33:
            raise ValueError("c1 and c2 must be 33 bytes")
        if len(pk_bytes) != 64:
            raise ValueError("pk must be 64 bytes")
        if len(pcm_bytes) != 64:
            raise ValueError("pedersen_commitment must be 64 bytes")
        if len(elgamal_blinding_bytes) != 32:
            raise ValueError("elgamal_blinding must be 32 bytes")
        if len(pedersen_blinding_bytes) != 32:
            raise ValueError("pedersen_blinding must be 32 bytes")
        if len(context_id_bytes) != 32:
            raise ValueError("context_id must be 32 bytes")

        # Parse points
        c1_pk = ffi.new("secp256k1_pubkey *")
        c2_pk = ffi.new("secp256k1_pubkey *")
        pk = ffi.new("secp256k1_pubkey *")
        pcm = ffi.new("secp256k1_pubkey *")

        lib.secp256k1_ec_pubkey_parse(self.ctx, c1_pk, c1_bytes, 33)
        lib.secp256k1_ec_pubkey_parse(self.ctx, c2_pk, c2_bytes, 33)

        pk_with_prefix = b"\x04" + pk_bytes
        lib.secp256k1_ec_pubkey_parse(self.ctx, pk, pk_with_prefix, 65)

        # Parse uncompressed Pedersen commitment (add 0x04 prefix)
        pcm_with_prefix = b"\x04" + pcm_bytes
        lib.secp256k1_ec_pubkey_parse(self.ctx, pcm, pcm_with_prefix, 65)

        # Generate proof
        proof = ffi.new("unsigned char[195]")
        result = lib.secp256k1_elgamal_pedersen_link_prove(
            self.ctx,
            proof,
            c1_pk,
            c2_pk,
            pk,
            pcm,
            amount,
            elgamal_blinding_bytes,
            pedersen_blinding_bytes,
            context_id_bytes,
        )
        if result != 1:
            raise RuntimeError("Failed to create ElGamal-Pedersen link proof")

        return bytes(proof[0:195]).hex().upper()

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
        """
        Create a balance link proof (uses SWAPPED parameter order).

        This is specifically for proving the link between the current balance
        ciphertext (from ledger) and the balance commitment.

        The verification function expects: (pk, c2, c1, pcm, context)
        So the proof generation must use the same order.

        Args:
            pk_uncompressed: 128-char hex string (64-byte public key, FIRST - swapped!)
            c2: 66-char hex string (33-byte compressed C2 point, SECOND - swapped!)
            c1: 66-char hex string (33-byte compressed C1 point, THIRD - swapped!)
            pedersen_commitment: 128-char hex string (64-byte Pedersen commitment, X + Y)
            amount: The plaintext balance amount
            private_key: 64-char hex string (32-byte ElGamal private key, NOT blinding!)
            pedersen_blinding: 64-char hex string (32-byte Pedersen blinding factor rho)
            context_id: 64-char hex string (32-byte transaction context ID)

        Returns:
            390-char hex string (195-byte balance link proof)
        """
        # Convert hex strings to bytes
        pk_bytes = bytes.fromhex(pk_uncompressed)
        c2_bytes = bytes.fromhex(c2)
        c1_bytes = bytes.fromhex(c1)
        pcm_bytes = bytes.fromhex(pedersen_commitment)
        private_key_bytes = bytes.fromhex(private_key)
        pedersen_blinding_bytes = bytes.fromhex(pedersen_blinding)
        context_id_bytes = bytes.fromhex(context_id)

        if len(c1_bytes) != 33 or len(c2_bytes) != 33:
            raise ValueError("c1 and c2 must be 33 bytes")
        if len(pk_bytes) != 64:
            raise ValueError("pk must be 64 bytes")
        if len(pcm_bytes) != 64:
            raise ValueError("pedersen_commitment must be 64 bytes")
        if len(private_key_bytes) != 32:
            raise ValueError("private_key must be 32 bytes")
        if len(pedersen_blinding_bytes) != 32:
            raise ValueError("pedersen_blinding must be 32 bytes")
        if len(context_id_bytes) != 32:
            raise ValueError("context_id must be 32 bytes")

        # Parse points
        c1_pk = ffi.new("secp256k1_pubkey *")
        c2_pk = ffi.new("secp256k1_pubkey *")
        pk = ffi.new("secp256k1_pubkey *")
        pcm = ffi.new("secp256k1_pubkey *")

        lib.secp256k1_ec_pubkey_parse(self.ctx, c1_pk, c1_bytes, 33)
        lib.secp256k1_ec_pubkey_parse(self.ctx, c2_pk, c2_bytes, 33)

        pk_with_prefix = b"\x04" + pk_bytes
        lib.secp256k1_ec_pubkey_parse(self.ctx, pk, pk_with_prefix, 65)

        # Parse uncompressed Pedersen commitment (add 0x04 prefix)
        pcm_with_prefix = b"\x04" + pcm_bytes
        lib.secp256k1_ec_pubkey_parse(self.ctx, pcm, pcm_with_prefix, 65)

        # Generate proof with SWAPPED order: pk, c2, c1 (not c1, c2, pk)
        proof = ffi.new("unsigned char[195]")
        result = lib.secp256k1_elgamal_pedersen_link_prove(
            self.ctx,
            proof,
            pk,  # PK FIRST (swapped!)
            c2_pk,  # C2 second (swapped!)
            c1_pk,  # C1 third (swapped!)
            pcm,
            amount,
            private_key_bytes,  # Use private key, not blinding factor
            pedersen_blinding_bytes,
            context_id_bytes,
        )
        if result != 1:
            raise RuntimeError("Failed to create balance link proof")

        return bytes(proof[0:195]).hex().upper()

    def create_equality_plaintext_proof(
        self,
        pk_uncompressed: str,
        c2: str,
        c1: str,
        amount: int,
        blinding_factor: str,
        context_id: str,
    ) -> str:
        """
        Create an equality proof for ConfidentialMPTClawback.

        Proves that the issuer knows the blinding factor r such that:
        - C1 = r*G
        - C2 = amount*G + r*PK

        This allows the issuer to prove they know the exact encrypted balance
        without revealing the blinding factor.

        Args:
            pk_uncompressed: 128-char hex string (64-byte public key, issuer's)
            c2: 66-char hex string (33-byte compressed C2 point)
            c1: 66-char hex string (33-byte compressed C1 point)
            amount: The plaintext amount
            blinding_factor: 64-char hex string (32-byte blinding factor used to encrypt)
            context_id: 64-char hex string (32-byte transaction context ID)

        Returns:
            196-char hex string (98-byte equality proof)
        """
        # Convert hex strings to bytes
        pk_bytes = bytes.fromhex(pk_uncompressed)
        c2_bytes = bytes.fromhex(c2)
        c1_bytes = bytes.fromhex(c1)
        blinding_bytes = bytes.fromhex(blinding_factor)
        context_id_bytes = bytes.fromhex(context_id)

        if len(c1_bytes) != 33 or len(c2_bytes) != 33:
            raise ValueError("c1 and c2 must be 33 bytes")
        if len(pk_bytes) != 64:
            raise ValueError("pk must be 64 bytes")
        if len(blinding_bytes) != 32:
            raise ValueError("blinding_factor must be 32 bytes")
        if len(context_id_bytes) != 32:
            raise ValueError("context_id must be 32 bytes")

        # Parse points
        c1_pk = ffi.new("secp256k1_pubkey *")
        c2_pk = ffi.new("secp256k1_pubkey *")
        pk = ffi.new("secp256k1_pubkey *")

        lib.secp256k1_ec_pubkey_parse(self.ctx, c1_pk, c1_bytes, 33)
        lib.secp256k1_ec_pubkey_parse(self.ctx, c2_pk, c2_bytes, 33)

        pk_with_prefix = b"\x04" + pk_bytes
        lib.secp256k1_ec_pubkey_parse(self.ctx, pk, pk_with_prefix, 65)

        # Generate equality proof
        proof = ffi.new("unsigned char[98]")
        result = lib.secp256k1_equality_plaintext_prove(
            self.ctx,
            proof,
            pk,
            c2_pk,
            c1_pk,
            amount,
            blinding_bytes,
            context_id_bytes,
        )
        if result != 1:
            raise RuntimeError("Failed to create equality proof")

        return bytes(proof[0:98]).hex().upper()

    def create_same_plaintext_proof_multi(  # noqa: PLR0914
        self,
        amount: int,
        ciphertexts: list,  # List of (c1, c2, pk, blinding) tuples (hex strings)
        context_id: str,
    ) -> str:
        """
        Create a proof that multiple ciphertexts encrypt the same amount.

        Args:
            amount: The common plaintext amount
            ciphertexts: List of (c1, c2, pk_uncompressed, blinding) tuples (all hex strings)
                - c1: 66-char hex string (33-byte compressed point)
                - c2: 66-char hex string (33-byte compressed point)
                - pk_uncompressed: 128-char hex string (64-byte public key)
                - blinding: 64-char hex string (32-byte blinding factor)
            context_id: 64-char hex string (32-byte transaction context ID)

        Returns:
            Variable-length hex string proof
        """
        # Convert context_id to bytes
        context_id_bytes = bytes.fromhex(context_id)

        if len(context_id_bytes) != 32:
            raise ValueError("context_id must be 32 bytes")

        n = len(ciphertexts)
        if n < 2:
            raise ValueError("Need at least 2 ciphertexts")

        # Allocate arrays
        R_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806
        S_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806
        Pk_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806
        r_array = ffi.new(f"unsigned char[{n * 32}]")

        # Parse all ciphertexts
        for i, (c1, c2, pk_uncompressed, blinding) in enumerate(ciphertexts):
            # Convert hex strings to bytes
            c1_bytes = bytes.fromhex(c1)
            c2_bytes = bytes.fromhex(c2)
            pk_bytes = bytes.fromhex(pk_uncompressed)
            blinding_bytes = bytes.fromhex(blinding)

            if len(c1_bytes) != 33 or len(c2_bytes) != 33:
                raise ValueError(f"Ciphertext {i}: c1 and c2 must be 33 bytes")
            if len(pk_bytes) != 64:
                raise ValueError(f"Ciphertext {i}: pk must be 64 bytes")
            if len(blinding_bytes) != 32:
                raise ValueError(f"Ciphertext {i}: blinding must be 32 bytes")

            lib.secp256k1_ec_pubkey_parse(self.ctx, R_array + i, c1_bytes, 33)
            lib.secp256k1_ec_pubkey_parse(self.ctx, S_array + i, c2_bytes, 33)

            pk_with_prefix = b"\x04" + pk_bytes
            lib.secp256k1_ec_pubkey_parse(self.ctx, Pk_array + i, pk_with_prefix, 65)

            # Copy blinding factor
            for j in range(32):
                r_array[i * 32 + j] = blinding_bytes[j]

        # Calculate proof size
        proof_size = lib.secp256k1_mpt_prove_same_plaintext_multi_size(n)
        proof_out = ffi.new(f"unsigned char[{proof_size}]")
        proof_len = ffi.new("size_t *", proof_size)

        # Generate proof
        result = lib.secp256k1_mpt_prove_same_plaintext_multi(
            self.ctx,
            proof_out,
            proof_len,
            amount,
            n,
            R_array,
            S_array,
            Pk_array,
            r_array,
            context_id_bytes,
        )
        if result != 1:
            raise RuntimeError("Failed to create same plaintext proof")

        return bytes(proof_out[0 : proof_len[0]]).hex().upper()
