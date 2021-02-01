"""Derived UInt class for serializing/deserializing 64 bit UInt."""
from __future__ import annotations

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.uint import UInt

_WIDTH = 8  # 64 / 8


class UInt64(UInt):
    """Derived UInt class for serializing/deserializing 64 bit UInt."""

    def __init__(self: UInt64, buffer: bytes = bytes(_WIDTH)) -> None:
        """Construct a new UInt64 type from a `bytes` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(cls: UInt64, parser: BinaryParser) -> UInt64:
        """Construct a new UInt64 type from a BinaryParser."""
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls: UInt64, value: int) -> UInt64:
        """Construct a new UInt64 type from a number."""
        if isinstance(value, int):
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big", signed=False)
            return cls(value_bytes)

        raise XRPLBinaryCodecException("Cannot construct UInt64 from given value")
