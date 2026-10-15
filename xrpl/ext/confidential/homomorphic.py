"""
Homomorphic operations on EC-ElGamal ciphertexts.

ElGamal is additively homomorphic: ``Enc(a) +/- Enc(b) = Enc(a +/- b)`` when both
ciphertexts are encrypted under the same public key. These wrap mpt-crypto's
``secp256k1_elgamal_add`` / ``secp256k1_elgamal_subtract``.

They are the building block for predicting a confidential balance's next state
client-side -- e.g. the ``new CB_S = CB_S - SenderEncryptedAmount`` update
rippled applies to a sender's ConfidentialBalanceSpending on a send (see
rippled's ``chainAfterSend`` / ``homomorphicSubtract``). That prediction lets a
client chain proofs for multiple same-(account, token) confidential transfers in
a single Batch: each subsequent inner transaction's proof must bind to the
balance *after* the previous one applies, not the stale on-ledger value.

Ciphertexts are represented here as (c1, c2) hex-string pairs -- each a 66-char
hex string encoding a 33-byte compressed point -- matching ``encryption.py``.
"""

from typing import Tuple

from xrpl.ext.confidential.crypto_bindings import SECP256K1_EC_COMPRESSED, ffi, lib

# A compressed secp256k1 point is 33 bytes = 66 hex characters.
_POINT_HEX_LEN = 66


def _parse_point(ctx: object, point_hex: str) -> object:
    """Parse a 66-char hex compressed point into a secp256k1_pubkey."""
    if len(point_hex) != _POINT_HEX_LEN:
        raise ValueError(
            f"ciphertext point must be {_POINT_HEX_LEN} hex chars (33 bytes)"
        )
    point_bytes = bytes.fromhex(point_hex)
    point = ffi.new("secp256k1_pubkey *")
    if lib.secp256k1_ec_pubkey_parse(ctx, point, point_bytes, len(point_bytes)) != 1:
        raise RuntimeError("Failed to parse ElGamal ciphertext point")
    return point


def _serialize_point(ctx: object, point: object) -> str:
    """Serialize a secp256k1_pubkey to a 66-char hex compressed point."""
    out = ffi.new("unsigned char[33]")
    out_len = ffi.new("size_t *", 33)
    result = lib.secp256k1_ec_pubkey_serialize(
        ctx, out, out_len, point, SECP256K1_EC_COMPRESSED
    )
    if result != 1 or out_len[0] != 33:
        raise RuntimeError("Failed to serialize ElGamal ciphertext point")
    return bytes(out[0:33]).hex().upper()


def _combine(
    a_c1: str, a_c2: str, b_c1: str, b_c2: str, *, subtract: bool
) -> Tuple[str, str]:
    """Parse both ciphertexts' points, apply the elgamal op, re-serialize."""
    ctx = lib.mpt_secp256k1_context()
    a1 = _parse_point(ctx, a_c1)
    a2 = _parse_point(ctx, a_c2)
    b1 = _parse_point(ctx, b_c1)
    b2 = _parse_point(ctx, b_c2)

    out_c1 = ffi.new("secp256k1_pubkey *")
    out_c2 = ffi.new("secp256k1_pubkey *")
    op = lib.secp256k1_elgamal_subtract if subtract else lib.secp256k1_elgamal_add
    if op(ctx, out_c1, out_c2, a1, a2, b1, b2) != 1:
        raise RuntimeError("Homomorphic ciphertext operation failed")

    return _serialize_point(ctx, out_c1), _serialize_point(ctx, out_c2)


def add_ciphertexts(a_c1: str, a_c2: str, b_c1: str, b_c2: str) -> Tuple[str, str]:
    """
    Homomorphically add two ElGamal ciphertexts under the same key:
    ``Enc(a) + Enc(b) = Enc(a + b)``.

    Predicts a balance credited by an inbound amount (e.g. a merged inbox).

    Args:
        a_c1: 66-char hex string (33-byte compressed C1 of the first ciphertext)
        a_c2: 66-char hex string (33-byte compressed C2 of the first ciphertext)
        b_c1: 66-char hex string (33-byte compressed C1 of the second ciphertext)
        b_c2: 66-char hex string (33-byte compressed C2 of the second ciphertext)

    Returns:
        (c1, c2) of the summed ciphertext, each a 66-char hex string.
    """
    return _combine(a_c1, a_c2, b_c1, b_c2, subtract=False)


def subtract_ciphertexts(a_c1: str, a_c2: str, b_c1: str, b_c2: str) -> Tuple[str, str]:
    """
    Homomorphically subtract two ElGamal ciphertexts under the same key:
    ``Enc(a) - Enc(b) = Enc(a - b)``.

    This is the rule rippled applies to a sender's ConfidentialBalanceSpending on
    a send (``new CB_S = CB_S - SenderEncryptedAmount``; see chainAfterSend). Use
    it to predict the next spending balance when chaining proofs for multiple
    same-(account, token) confidential transfers in one Batch.

    Args:
        a_c1: 66-char hex string (33-byte compressed C1 of the minuend ciphertext)
        a_c2: 66-char hex string (33-byte compressed C2 of the minuend ciphertext)
        b_c1: 66-char hex string (33-byte compressed C1 of the subtrahend)
        b_c2: 66-char hex string (33-byte compressed C2 of the subtrahend)

    Returns:
        (c1, c2) of the difference ciphertext, each a 66-char hex string.
    """
    return _combine(a_c1, a_c2, b_c1, b_c2, subtract=True)
