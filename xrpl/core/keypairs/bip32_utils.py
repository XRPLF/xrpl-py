"""BIP32/BIP44 key derivation for use with BIP39 mnemonics."""

from __future__ import annotations

import hashlib
import hmac
import struct
import unicodedata
from typing import Tuple

from ecpy.curves import Curve  # type: ignore
from ecpy.keys import ECPrivateKey  # type: ignore
from typing_extensions import Final

from xrpl.core.keypairs.exceptions import XRPLKeypairsException
from xrpl.core.keypairs.secp256k1 import SECP256K1

_CURVE: Final[Curve] = Curve.get_curve("secp256k1")
_GROUP_ORDER: Final[int] = _CURVE.order
_HARDENED: Final[int] = 0x80000000
_XRP_COIN_TYPE: Final[int] = 144
_KEY_LENGTH: Final[int] = 66
_PADDING_PREFIX: Final[str] = "0"
_VERIFICATION_MESSAGE: Final[bytes] = b"This test message should verify."


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """
    Convert a BIP39 mnemonic phrase to a 64-byte seed.

    Args:
        mnemonic: A BIP39 mnemonic phrase (space-separated words).
        passphrase: An optional passphrase for additional security.

    Returns:
        A 64-byte seed derived from the mnemonic.
    """
    normalized_mnemonic = unicodedata.normalize("NFKD", mnemonic)
    normalized_passphrase = unicodedata.normalize("NFKD", passphrase)
    return hashlib.pbkdf2_hmac(
        "sha512",
        normalized_mnemonic.encode("utf-8"),
        ("mnemonic" + normalized_passphrase).encode("utf-8"),
        2048,
        dklen=64,
    )


def _derive_master_key(seed: bytes) -> Tuple[bytes, bytes]:
    """Derive master private key and chain code from a BIP39 seed."""
    h = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    return h[:32], h[32:]


def _derive_child_key(
    parent_key: bytes, parent_chain_code: bytes, index: int
) -> Tuple[bytes, bytes]:
    """Derive a child key from a parent key using BIP32 derivation."""
    if index >= _HARDENED:
        data = b"\x00" + parent_key + struct.pack(">I", index)
    else:
        private_int = int.from_bytes(parent_key, "big")
        ec_private = ECPrivateKey(private_int, _CURVE)
        pub_point = ec_private.get_public_key()
        pub_bytes = bytes(_CURVE.encode_point(pub_point.W, compressed=True))
        data = pub_bytes + struct.pack(">I", index)

    h = hmac.new(parent_chain_code, data, hashlib.sha512).digest()
    il_int = int.from_bytes(h[:32], "big")
    if il_int >= _GROUP_ORDER:
        raise ValueError("Derived key is invalid (IL >= group order).")
    child_key_int = (il_int + int.from_bytes(parent_key, "big")) % _GROUP_ORDER
    if child_key_int == 0:
        raise ValueError("Derived key is invalid (zero key).")
    return child_key_int.to_bytes(32, "big"), h[32:]


def derive_keypair_from_mnemonic(
    mnemonic: str,
    passphrase: str = "",
    account_index: int = 0,
    address_index: int = 0,
) -> Tuple[str, str]:
    """
    Derive a secp256k1 keypair from a BIP39 mnemonic using the BIP44 path
    ``m/44'/144'/account'/0/address_index``.

    Args:
        mnemonic: A BIP39 mnemonic phrase (space-separated words).
        passphrase: An optional BIP39 passphrase. The default is ``""``.
        account_index: The BIP44 account index. The default is ``0``.
        address_index: The BIP44 address index. The default is ``0``.

    Returns:
        A (public_key, private_key) tuple as uppercase hex strings.
    """
    if not 0 <= account_index < _HARDENED:
        raise ValueError(
            f"account_index must be in range [0, {_HARDENED}), got {account_index}"
        )
    if not 0 <= address_index < _HARDENED:
        raise ValueError(
            f"address_index must be in range [0, {_HARDENED}), got {address_index}"
        )

    seed = mnemonic_to_seed(mnemonic, passphrase)
    key, chain_code = _derive_master_key(seed)

    for index in [
        44 + _HARDENED,
        _XRP_COIN_TYPE + _HARDENED,
        account_index + _HARDENED,
        0,
        address_index,
    ]:
        key, chain_code = _derive_child_key(key, chain_code, index)

    private_int = int.from_bytes(key, "big")
    ec_private = ECPrivateKey(private_int, _CURVE)
    ec_public = ec_private.get_public_key()

    pub_bytes = bytes(_CURVE.encode_point(ec_public.W, compressed=True))
    public_key = pub_bytes.hex().rjust(_KEY_LENGTH, _PADDING_PREFIX).upper()
    private_key = key.hex().rjust(_KEY_LENGTH, _PADDING_PREFIX).upper()

    signature = SECP256K1.sign(_VERIFICATION_MESSAGE, private_key)
    if not SECP256K1.is_valid_message(_VERIFICATION_MESSAGE, signature, public_key):
        raise XRPLKeypairsException(
            "Derived keypair did not generate verifiable signature",
        )

    return public_key, private_key
