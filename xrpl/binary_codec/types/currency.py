"""Codec for currency property inside an XRPL issued currency amount json."""
from __future__ import annotations

import re

from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.hash160 import Hash160

_ISO_REGEX = "^[A-Z0-9]{3}$"
_HEX_REGEX = "^[A-F0-9]{40}$"


def is_iso_code(value: str) -> bool:
    """Tests if value is a valid 3-char iso code."""
    pattern = re.compile(_ISO_REGEX)
    return pattern.match(value)


def is_hex(value: str) -> bool:
    """Tests if value is a valid 40-char hex string."""
    pattern = re.compile(_HEX_REGEX)
    return pattern.match(value)


def iso_to_bytes(iso: str) -> bytes:
    """
    Convert an ISO code to a 160-bit (20 byte) encoded representation.

    See "Currency codes" subheading in
    `Amount Fields <https://xrpl.org/serialization.html#amount-fields>`_
    """
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


def is_string_representation(value: str) -> bool:
    """Tests if value is a valid string representation of a currency."""
    return is_iso_code(value) or is_hex(value)


def is_bytes_array(buffer: bytes) -> bool:
    """Tests if a bytes object is a valid representation of a currency."""
    return len(buffer) == 20


# TODO: the type of param `value` is (bytes | str)... how to represent this?
def is_valid_representation(value) -> bool:
    """Ensures that a value is a valid representation of a currency."""
    if type(value) == "bytes":
        is_bytes_array(value)
    else:
        is_string_representation(value)


def bytes_from_representation(value: str) -> bytes:
    """Generate bytes from a string or buffer representation of a currency."""
    if not is_valid_representation(value):
        raise XRPLBinaryCodecException(
            "Unsupported Currency representation: {}".format(value)
        )
    if len(value) == 3:
        return iso_to_bytes(value)
    return bytes.fromhex(value)


class Currency(Hash160):
    """
    Defines how to encode and decode currency codes in issued currency amounts.
    `Amount fields <https://xrpl.org/serialization.html#amount-fields>`_
    """

    # static readonly XRP = new Currency(Buffer.alloc(20));
    # private readonly _iso?: string;
    # private readonly _isNative: boolean;

    def __init__(self, buffer: bytes = None) -> None:
        """Construct a Currency."""
        if buffer is not None:
            self.buffer = buffer
        else:
            self.buffer = bytes(20)

        #        let onlyISO = true;
        #
        # const bytes = this.bytes;
        # const code = this.bytes.slice(12, 15);
        # const iso = code.toString();
        #
        # for (let i = bytes.length - 1; i >= 0; i--) {
        #   if (bytes[i] !== 0 && !(i === 12 || i === 13 || i === 14)) {
        #     onlyISO = false;
        #     break;
        #   }
        # }
        #
        # const lossLessISO = onlyISO && iso !== "XRP" && ISO_REGEX.test(iso);
        # this._isNative = onlyISO && code.toString("hex") === "000000";
        # this._iso = this._isNative ? "XRP" : lossLessISO ? iso : undefined;

    def from_parser(self, parser, length_hint: int = None) -> Currency:
        """Construct a Currency from an existing BinaryParser."""
        pass

    def from_value(self, value: str) -> Currency:
        """Construct a Currency object from a string representation of a currency."""
        # TODO: error/format checking?
        return Currency(bytes_from_representation(value))

    def is_native(self) -> bool:
        """Tells if this currency is native."""
        return self._is_native

    # TODO: this method actually returns str or None... how to rep this?
    def iso(self) -> str:
        """Return the ISO code of this currency if it exists, else None."""
        return self._iso

    def to_json(self) -> str:
        """Returns the JSON representation of a currency."""
        iso = self.iso()
        if iso is not None:
            return iso
        return self.buffer.hex().upper()
