"""Codec for serializing and deserializing AccountID fields."""
from __future__ import annotations  # Requires Python 3.7+

import re

from xrpl.addresscodec import decode_classic_address, encode_classic_address
from xrpl.binary_codec.types.hash160 import Hash160

_HEX_REGEX = re.compile("^[A-F0-9]{40}$")


class AccountID(Hash160):
    """Codec for serializing and deserializing AccountID fields."""

    def __init__(self, buffer: bytes = None) -> None:
        """
        Construct an AccountID from given bytes.
        If buffer is not provided, default to 20 zero bytes.
        """
        if buffer is not None:
            super().__init__(buffer)
        else:
            super().__init__(bytes(20))

    @classmethod
    def from_value(cls, value: str) -> AccountID:
        """Construct an AccountID from a hex string or a base58 r-Address."""
        if value == "":
            return cls()

        # hex-encoded case
        if _HEX_REGEX.fullmatch(value):
            return cls(bytes.fromhex(value))
        # base58 case
        return cls(decode_classic_address(value))

    def to_json(self) -> str:
        """Return the value of this AccountID encoded as a base58 string."""
        return encode_classic_address(self.buffer)
