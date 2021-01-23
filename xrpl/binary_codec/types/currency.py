"""Codec for currency property inside an XRPL issued currency amount json."""
from __future__ import annotations

import re

from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.hash160 import Hash160

_ISO_REGEX = "^[A-Z0-9]{3}$"
_HEX_REGEX = "^[A-F0-9]{40}$"


def _is_iso_code(value: str) -> bool:
    """Tests if value is a valid 3-char iso code."""
    pattern = re.compile(_ISO_REGEX)
    return bool(pattern.fullmatch(value))


def _is_hex(value: str) -> bool:
    """Tests if value is a valid 40-char hex string."""
    pattern = re.compile(_HEX_REGEX)
    return bool(pattern.fullmatch(value))


def _iso_to_bytes(iso: str) -> bytes:
    """
    Convert an ISO code to a 160-bit (20 byte) encoded representation.

    See "Currency codes" subheading in
    `Amount Fields <https://xrpl.org/serialization.html#amount-fields>`_
    """
    if not _is_iso_code(iso):
        raise XRPLBinaryCodecException("Invalid ISO code: {}".format(iso))

    if iso == "XRP":
        # This code (160 bit all zeroes) is used to indicate XRP in
        # rare cases where a field must specify a currency code for XRP.
        return bytes(20)

    iso_bytes = iso.encode("ASCII")
    # Currency Codes: https://xrpl.org/currency-formats.html#standard-currency-codes
    # 160 total bits:
    #   8 bits type code (0x00)
    #   88 bits reserved (0's)
    #   24 bits ASCII
    #   16 bits version (0x00)
    #   24 bits reserved (0's)
    return bytes(12) + iso_bytes + bytes(5)


class Currency(Hash160):
    """
    Defines how to encode and decode currency codes in issued currency amounts.
    `Amount fields <https://xrpl.org/serialization.html#amount-fields>`_

    Attributes:
        buffer: The byte encoding of this currency.
        _iso: The three-character ISO currency code if standard format, else None.
        _is_native: True if the currency code is "XRP"
    """

    def __init__(self, buffer: bytes = None) -> None:
        """Construct a Currency."""
        if buffer is not None:
            super().__init__(buffer)
        else:
            super().__init__(bytes(20))

        # Determine whether this currency code is in standard or nonstandard format:
        # https://xrpl.org/currency-formats.html#nonstandard-currency-codes
        is_standard_code = True
        first_12_bytes = self.buffer[:12]
        code_bytes = self.buffer[12:15]
        last_5_bytes = self.buffer[15:]
        iso = code_bytes.decode("ascii")

        if not (first_12_bytes == bytes(12)) or not (last_5_bytes == bytes(5)):
            is_standard_code = False

        lossless_iso = is_standard_code and iso != "XRP" and _is_iso_code(iso)
        self._is_native = is_standard_code and code_bytes.hex() == "000000"
        if self._is_native:
            self._iso = "XRP"
        else:
            if lossless_iso:
                self._iso = iso
            else:
                self._iso = None

    @classmethod
    def from_value(cls, value: str) -> Currency:
        """Construct a Currency object from a string representation of a currency."""
        if _is_iso_code(value):
            return Currency(_iso_to_bytes(value))
        if _is_hex(value):
            return cls(bytes.fromhex(value))
        raise XRPLBinaryCodecException(
            "Unsupported Currency representation: {}".format(value)
        )

    def to_json(self) -> str:
        """Returns the JSON representation of a currency."""
        if self._iso is not None:
            return self._iso
        return self.buffer.hex().upper()
